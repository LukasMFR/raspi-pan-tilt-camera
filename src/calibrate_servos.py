#!/usr/bin/env python3

from adafruit_servokit import ServoKit

from pan_tilt_config import CONFIG_PATH, load_config, save_config


STEP_SMALL = 1
STEP_LARGE = 5


def clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))


def movement_delta(base_delta, inverted):
    return -base_delta if inverted else base_delta


config = load_config()

pan = config["pan_center"]
tilt = config["tilt_center"]

kit = ServoKit(channels=16)

for ch in (config["pan_channel"], config["tilt_channel"]):
    kit.servo[ch].set_pulse_width_range(500, 2500)


def apply():
    global pan, tilt

    pan = clamp(pan, config["pan_min"], config["pan_max"])
    tilt = clamp(tilt, config["tilt_min"], config["tilt_max"])

    kit.servo[config["pan_channel"]].angle = pan
    kit.servo[config["tilt_channel"]].angle = tilt

    print(
        f"PAN={pan} deg | TILT={tilt} deg | "
        f"invert_pan={config['invert_pan']} | invert_tilt={config['invert_tilt']}"
    )


def save():
    config["pan_center"] = pan
    config["tilt_center"] = tilt
    save_config(config)
    print(f"Config saved to {CONFIG_PATH}")


print(f"""
Pan/tilt calibration

Config file:
  {CONFIG_PATH}

Movement:
  a/d = left/right by 1 deg
  w/s = up/down by 1 deg
  A/D/W/S = same directions by 5 deg

Other:
  p = toggle pan inversion
  t = toggle tilt inversion
  c = return to configured center
  x = save current position as center
  q = quit

If a direction moves backwards, press p or t for that axis and try again.
Move the camera to its visual center, then press x.
""")

apply()

while True:
    cmd = input("> ").strip()

    if cmd in {"a", "d", "w", "s", "A", "D", "W", "S"}:
        amount = STEP_LARGE if cmd.isupper() else STEP_SMALL
        key = cmd.lower()

        if key == "a":
            pan += movement_delta(-amount, config["invert_pan"])
        elif key == "d":
            pan += movement_delta(amount, config["invert_pan"])
        elif key == "w":
            tilt += movement_delta(-amount, config["invert_tilt"])
        elif key == "s":
            tilt += movement_delta(amount, config["invert_tilt"])

    elif cmd == "p":
        config["invert_pan"] = not config["invert_pan"]
    elif cmd == "t":
        config["invert_tilt"] = not config["invert_tilt"]
    elif cmd == "c":
        pan = config["pan_center"]
        tilt = config["tilt_center"]
    elif cmd == "x":
        save()
        continue
    elif cmd == "q":
        break
    else:
        print("Unknown command.")
        continue

    apply()
