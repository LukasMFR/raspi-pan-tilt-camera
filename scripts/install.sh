#!/usr/bin/env bash
set -e

sudo apt update
sudo apt install -y \
  git \
  i2c-tools \
  python3-pip \
  python3-venv \
  python3-smbus \
  python3-flask \
  python3-picamera2

python3 -m venv ~/servo-env --system-site-packages
~/servo-env/bin/pip install --upgrade pip
~/servo-env/bin/pip install -r requirements.txt

echo "Installation terminée."
echo "Pense à activer I2C avec : sudo raspi-config"
