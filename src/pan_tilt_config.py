#!/usr/bin/env python3

import json
import os
from pathlib import Path


CONFIG_PATH = Path(
    os.environ.get("PAN_TILT_CONFIG", Path.home() / "pan_tilt_config.json")
)

DEFAULT_CONFIG = {
    "pan_channel": 1,
    "tilt_channel": 0,
    "pan_center": 90,
    "tilt_center": 90,
    "pan_min": 30,
    "pan_max": 150,
    "tilt_min": 45,
    "tilt_max": 135,
    "invert_pan": False,
    "invert_tilt": False,
}


def _as_int(config, key):
    try:
        return int(config[key])
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{key} must be an integer") from exc


def _as_bool(config, key):
    value = config[key]
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        value = value.strip().lower()
        if value in {"1", "true", "yes", "on"}:
            return True
        if value in {"0", "false", "no", "off"}:
            return False
    raise ValueError(f"{key} must be true or false")


def validate_config(config):
    normalized = {
        "pan_channel": _as_int(config, "pan_channel"),
        "tilt_channel": _as_int(config, "tilt_channel"),
        "pan_center": _as_int(config, "pan_center"),
        "tilt_center": _as_int(config, "tilt_center"),
        "pan_min": _as_int(config, "pan_min"),
        "pan_max": _as_int(config, "pan_max"),
        "tilt_min": _as_int(config, "tilt_min"),
        "tilt_max": _as_int(config, "tilt_max"),
        "invert_pan": _as_bool(config, "invert_pan"),
        "invert_tilt": _as_bool(config, "invert_tilt"),
    }

    for key in ("pan_channel", "tilt_channel"):
        if not 0 <= normalized[key] <= 15:
            raise ValueError(f"{key} must be between 0 and 15")

    if normalized["pan_channel"] == normalized["tilt_channel"]:
        raise ValueError("pan_channel and tilt_channel must be different")

    for axis in ("pan", "tilt"):
        min_key = f"{axis}_min"
        max_key = f"{axis}_max"
        center_key = f"{axis}_center"

        if not 0 <= normalized[min_key] <= 180:
            raise ValueError(f"{min_key} must be between 0 and 180")
        if not 0 <= normalized[max_key] <= 180:
            raise ValueError(f"{max_key} must be between 0 and 180")
        if normalized[min_key] >= normalized[max_key]:
            raise ValueError(f"{min_key} must be less than {max_key}")
        if not normalized[min_key] <= normalized[center_key] <= normalized[max_key]:
            raise ValueError(f"{center_key} must be between {min_key} and {max_key}")

    return normalized


def load_config(path=CONFIG_PATH):
    config = DEFAULT_CONFIG.copy()

    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError(f"{path} must contain a JSON object")
        config.update(data)
    else:
        print(f"Config not found: {path}")
        print("Using built-in defaults.")

    return validate_config(config)


def save_config(config, path=CONFIG_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = validate_config(config)
    path.write_text(json.dumps(normalized, indent=2) + "\n", encoding="utf-8")
