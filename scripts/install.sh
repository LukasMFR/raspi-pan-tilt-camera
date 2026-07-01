#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_USER="${SUDO_USER:-$USER}"
APP_HOME="$(getent passwd "$APP_USER" | cut -d: -f6)"
VENV_DIR="$APP_HOME/servo-env"
CONFIG_PATH="${PAN_TILT_CONFIG:-$APP_HOME/pan_tilt_config.json}"
SERVICE_NAME="raspi-pan-tilt-camera.service"
SERVICE_PATH="/etc/systemd/system/$SERVICE_NAME"

cd "$ROOT_DIR"

run_as_app_user() {
  if [ "$(id -u)" -eq 0 ]; then
    sudo -u "$APP_USER" "$@"
  else
    "$@"
  fi
}

sudo apt update
sudo apt install -y \
  git \
  i2c-tools \
  python3-pip \
  python3-venv \
  python3-smbus \
  python3-flask \
  python3-picamera2

if command -v raspi-config >/dev/null 2>&1; then
  sudo raspi-config nonint do_i2c 0
fi

run_as_app_user python3 -m venv "$VENV_DIR" --system-site-packages
run_as_app_user "$VENV_DIR/bin/pip" install --upgrade pip
run_as_app_user "$VENV_DIR/bin/pip" install -r requirements.txt

if [ ! -f "$CONFIG_PATH" ]; then
  run_as_app_user mkdir -p "$(dirname "$CONFIG_PATH")"
  run_as_app_user install -m 0644 config/pan_tilt_config.example.json "$CONFIG_PATH"
  echo "Created config: $CONFIG_PATH"
else
  echo "Config already exists: $CONFIG_PATH"
fi

for group in i2c gpio video render; do
  if getent group "$group" >/dev/null; then
    sudo usermod -aG "$group" "$APP_USER"
  fi
done

tmp_service="$(mktemp)"
sed \
  -e "s|^User=.*|User=$APP_USER|" \
  -e "s|^WorkingDirectory=.*|WorkingDirectory=$ROOT_DIR|" \
  -e "s|^Environment=PAN_TILT_CONFIG=.*|Environment=PAN_TILT_CONFIG=$CONFIG_PATH|" \
  -e "s|^ExecStart=.*|ExecStart=$VENV_DIR/bin/python $ROOT_DIR/src/app.py|" \
  systemd/$SERVICE_NAME > "$tmp_service"
sudo install -m 0644 "$tmp_service" "$SERVICE_PATH"
rm -f "$tmp_service"
sudo systemctl daemon-reload

echo
echo "Installation complete."
echo "If this user was newly added to hardware groups, reboot before running the app."
echo
echo "Next steps:"
echo "  $VENV_DIR/bin/python src/calibrate_servos.py"
echo "  scripts/run.sh"
echo
echo "Optional service startup:"
echo "  sudo systemctl enable --now $SERVICE_NAME"
