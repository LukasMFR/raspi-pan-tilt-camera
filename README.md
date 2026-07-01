# raspi-pan-tilt-camera

Raspberry Pi 3 B+ web camera stream with Adeept Robot HAT pan/tilt servo control.

The app uses:

- Raspberry Pi Camera with Picamera2
- Adeept Robot HAT / PCA9685 servo output
- Two pan/tilt servos
- Flask web UI

## Hardware Defaults

Default servo config:

- Pan servo: channel 1
- Tilt servo: channel 0
- Pan range: 30 to 150 deg
- Tilt range: 45 to 135 deg
- Center: 90 / 90 deg

These values are intentionally conservative. If a servo buzzes or pushes against an end stop, reduce the matching min/max before running the web app for long periods.

## First-Time Setup

Clone the repo on the Raspberry Pi, then run:

```bash
cd ~/raspi-pan-tilt-camera
scripts/install.sh
```

The installer:

- installs apt packages for I2C, Picamera2, Flask, and Python venv support
- enables I2C when `raspi-config` is available
- creates `~/servo-env`
- installs Python servo dependencies
- creates `~/pan_tilt_config.json` if it does not exist
- installs a matching systemd service file
- adds your user to common Pi hardware groups when they exist

Reboot after install if your user was newly added to hardware groups.

## Calibrate

Run calibration before starting the web app:

```bash
~/servo-env/bin/python src/calibrate_servos.py
```

Use `a/d/w/s` to move, `p` or `t` to toggle inversion if an axis moves backwards, and `x` to save the current position as the center.

The active config path defaults to:

```text
~/pan_tilt_config.json
```

You can override it with:

```bash
export PAN_TILT_CONFIG=/path/to/pan_tilt_config.json
```

## Run Manually

```bash
scripts/run.sh
```

Open:

```text
http://<raspberry-pi-ip>:5000
```

The web app has no login. Use it on a trusted local network only, and do not expose port 5000 to the internet.

## Run As A Service

After install and calibration:

```bash
sudo systemctl enable --now raspi-pan-tilt-camera.service
```

Useful service commands:

```bash
sudo systemctl status raspi-pan-tilt-camera.service
sudo journalctl -u raspi-pan-tilt-camera.service -f
sudo systemctl restart raspi-pan-tilt-camera.service
```

## Utility Scripts

- `src/calibrate_servos.py`: calibrate center and inversion
- `src/center_servos.py`: move both servos to the configured center
- `src/test_pan_tilt.py`: make small test movements within configured limits
- `src/app.py`: Flask app and MJPEG camera stream

## Notes

- `python3-picamera2` is installed through apt, not pip.
- The app should run as the normal Pi user, not as root.
- Keep the camera ribbon, HAT power, and servo power wiring checked before running automated movement.
