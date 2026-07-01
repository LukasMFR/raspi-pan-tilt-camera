#!/usr/bin/env python3

from time import sleep

from adafruit_servokit import ServoKit

from pan_tilt_config import load_config


config = load_config()
kit = ServoKit(channels=16)

positions = (
    (config["pan_channel"], config["pan_center"], "pan"),
    (config["tilt_channel"], config["tilt_center"], "tilt"),
)

for channel, angle, name in positions:
    kit.servo[channel].set_pulse_width_range(500, 2500)
    kit.servo[channel].angle = angle
    print(f"{name}: channel {channel} centered at {angle} deg")
    sleep(0.3)
