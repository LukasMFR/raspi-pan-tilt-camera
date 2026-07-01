#!/usr/bin/env python3

from time import sleep
from adafruit_servokit import ServoKit

kit = ServoKit(channels=16)

# Réglage classique pour petits servos type SG90.
# Si un servo force en butée, on réduira la plage après.
for ch in [0, 1]:
    kit.servo[ch].set_pulse_width_range(500, 2500)
    kit.servo[ch].angle = 90
    sleep(0.3)

print("Servos 0 et 1 centrés à 90°.")
