#!/usr/bin/env python3

from time import sleep

from adafruit_servokit import ServoKit

from pan_tilt_config import load_config


TEST_STEP = 15


def clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))


config = load_config()
kit = ServoKit(channels=16)

pan_channel = config["pan_channel"]
tilt_channel = config["tilt_channel"]

for ch in (pan_channel, tilt_channel):
    kit.servo[ch].set_pulse_width_range(500, 2500)


def move(pan, tilt):
    pan = clamp(pan, config["pan_min"], config["pan_max"])
    tilt = clamp(tilt, config["tilt_min"], config["tilt_max"])

    print(f"pan={pan}, tilt={tilt}")
    kit.servo[pan_channel].angle = pan
    kit.servo[tilt_channel].angle = tilt
    sleep(1)


pan_center = config["pan_center"]
tilt_center = config["tilt_center"]

move(pan_center, tilt_center)

move(pan_center - TEST_STEP, tilt_center)
move(pan_center + TEST_STEP, tilt_center)
move(pan_center, tilt_center)

move(pan_center, tilt_center - TEST_STEP)
move(pan_center, tilt_center + TEST_STEP)
move(pan_center, tilt_center)

print("Test complete.")
