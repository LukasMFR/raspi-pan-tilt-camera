#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."
sudo ~/servo-env/bin/python src/app.py
