#!/usr/bin/env python3

import json
from pathlib import Path
from adafruit_servokit import ServoKit

CONFIG_PATH = Path("/home/pi/pan_tilt_config.json")

# Canaux inversés selon ton montage
PAN_CH = 1
TILT_CH = 0

pan = 90
tilt = 90

PAN_MIN = 30
PAN_MAX = 150
TILT_MIN = 45
TILT_MAX = 135

kit = ServoKit(channels=16)

for ch in [PAN_CH, TILT_CH]:
    kit.servo[ch].set_pulse_width_range(500, 2500)

def clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))

def apply():
    global pan, tilt

    pan = clamp(pan, PAN_MIN, PAN_MAX)
    tilt = clamp(tilt, TILT_MIN, TILT_MAX)

    kit.servo[PAN_CH].angle = pan
    kit.servo[TILT_CH].angle = tilt

    print(f"PAN={pan}° | TILT={tilt}°")

def save():
    data = {
        "pan_channel": PAN_CH,
        "tilt_channel": TILT_CH,
        "pan_center": pan,
        "tilt_center": tilt,
        "pan_min": PAN_MIN,
        "pan_max": PAN_MAX,
        "tilt_min": TILT_MIN,
        "tilt_max": TILT_MAX,
        "invert_pan": True,
        "invert_tilt": True
    }

    CONFIG_PATH.write_text(json.dumps(data, indent=2))
    print(f"Config sauvegardée dans {CONFIG_PATH}")
    print(data)

print("""
Calibration caméra pan/tilt

Commandes corrigées :
  a = gauche
  d = droite
  w = haut
  s = bas

  A/D/W/S = mouvements de 5°

  c = revenir à 90/90
  x = sauvegarder le centre actuel
  q = quitter

Objectif :
  Mets la caméra visuellement droite.
  Puis appuie sur x pour sauvegarder.
""")

apply()

while True:
    cmd = input("> ").strip()

    # Gauche/droite inversés
    if cmd == "a":
        pan += 1
    elif cmd == "d":
        pan -= 1
    elif cmd == "A":
        pan += 5
    elif cmd == "D":
        pan -= 5

    # Haut/bas inversés
    elif cmd == "w":
        tilt += 1
    elif cmd == "s":
        tilt -= 1
    elif cmd == "W":
        tilt += 5
    elif cmd == "S":
        tilt -= 5

    elif cmd == "c":
        pan = 90
        tilt = 90
    elif cmd == "x":
        save()
        continue
    elif cmd == "q":
        break
    else:
        print("Commande inconnue.")
        continue

    apply()
