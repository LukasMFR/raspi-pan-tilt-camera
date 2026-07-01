#!/usr/bin/env python3

from time import sleep
from adafruit_servokit import ServoKit

kit = ServoKit(channels=16)

PAN = 0
TILT = 1

for ch in [PAN, TILT]:
    kit.servo[ch].set_pulse_width_range(500, 2500)

def move(pan, tilt):
    print(f"pan={pan}, tilt={tilt}")
    kit.servo[PAN].angle = pan
    kit.servo[TILT].angle = tilt
    sleep(1)

# Centre
move(90, 90)

# Petits mouvements safe
move(75, 90)
move(105, 90)
move(90, 90)

move(90, 75)
move(90, 105)
move(90, 90)

print("Test terminé.")
