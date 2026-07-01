#!/usr/bin/env python3

import io
import threading

from flask import Flask, Response, jsonify, render_template_string

from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import FileOutput

from adafruit_servokit import ServoKit

from pan_tilt_config import CONFIG_PATH, load_config


# =========================
# CONFIG
# =========================

WIDTH = 1280
HEIGHT = 720
FPS = 20
PORT = 5000
STEP = 5


config = load_config()

PAN_CH = int(config["pan_channel"])
TILT_CH = int(config["tilt_channel"])

PAN_CENTER = int(config["pan_center"])
TILT_CENTER = int(config["tilt_center"])

PAN_MIN = int(config["pan_min"])
PAN_MAX = int(config["pan_max"])
TILT_MIN = int(config["tilt_min"])
TILT_MAX = int(config["tilt_max"])

INVERT_PAN = bool(config["invert_pan"])
INVERT_TILT = bool(config["invert_tilt"])

pan = PAN_CENTER
tilt = TILT_CENTER
servo_lock = threading.Lock()


# =========================
# SERVOS
# =========================

kit = ServoKit(channels=16)

for ch in [PAN_CH, TILT_CH]:
    kit.servo[ch].set_pulse_width_range(500, 2500)


def clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))


def apply_servos():
    global pan, tilt

    pan = clamp(pan, PAN_MIN, PAN_MAX)
    tilt = clamp(tilt, TILT_MIN, TILT_MAX)

    kit.servo[PAN_CH].angle = pan
    kit.servo[TILT_CH].angle = tilt

    print(f"PAN={pan}° | TILT={tilt}°")


def move_servo(direction):
    global pan, tilt

    with servo_lock:
        pan_delta = -STEP
        tilt_delta = -STEP

        if INVERT_PAN:
            pan_delta *= -1
        if INVERT_TILT:
            tilt_delta *= -1

        if direction == "left":
            pan += pan_delta

        elif direction == "right":
            pan -= pan_delta

        elif direction == "up":
            tilt += tilt_delta

        elif direction == "down":
            tilt -= tilt_delta

        elif direction == "center":
            pan = PAN_CENTER
            tilt = TILT_CENTER

        apply_servos()


# Center the servos at startup.
with servo_lock:
    apply_servos()


# =========================
# WEB PAGE
# =========================

PAGE = """
<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Raspberry Pi Caméra Motorisée</title>

  <style>
    :root {
      color-scheme: dark;
    }

    body {
      margin: 0;
      min-height: 100vh;
      background:
        radial-gradient(circle at top, rgba(255,255,255,.08), transparent 35%),
        #0f0f12;
      color: white;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 18px;
      box-sizing: border-box;
    }

    .app {
      width: min(96vw, 1100px);
      display: flex;
      flex-direction: column;
      gap: 16px;
      align-items: center;
    }

    h1 {
      margin: 0;
      font-size: clamp(22px, 4vw, 34px);
      letter-spacing: 0;
    }

    .subtitle {
      margin: 0;
      color: rgba(255,255,255,.65);
      font-size: 14px;
      text-align: center;
    }

    .video-card {
      width: 100%;
      border-radius: 22px;
      overflow: hidden;
      background: #000;
      box-shadow: 0 24px 80px rgba(0,0,0,.55);
      border: 1px solid rgba(255,255,255,.08);
    }

    img {
      width: 100%;
      height: auto;
      display: block;
      background: #000;
    }

    .panel {
      width: min(100%, 560px);
      display: flex;
      flex-direction: column;
      gap: 12px;
      align-items: center;
      background: rgba(255,255,255,.06);
      border: 1px solid rgba(255,255,255,.10);
      border-radius: 22px;
      padding: 16px;
      backdrop-filter: blur(18px);
    }

    .controls {
      display: grid;
      grid-template-columns: 84px 84px 84px;
      gap: 10px;
      align-items: center;
      justify-content: center;
    }

    button {
      height: 58px;
      border: 0;
      border-radius: 16px;
      background: white;
      color: #111;
      font-size: 24px;
      font-weight: 800;
      cursor: pointer;
      box-shadow: 0 8px 20px rgba(0,0,0,.25);
    }

    button:active {
      transform: scale(.96);
    }

    .center {
      font-size: 13px;
      letter-spacing: .02em;
    }

    .empty {
      height: 58px;
    }

    .status {
      font-size: 14px;
      color: rgba(255,255,255,.75);
      text-align: center;
      line-height: 1.5;
    }

    .small {
      font-size: 12px;
      color: rgba(255,255,255,.48);
      text-align: center;
    }
  </style>
</head>

<body>
  <main class="app">
    <div>
      <h1>Caméra Raspberry Pi</h1>
      <p class="subtitle">Stream local + contrôle pan/tilt</p>
    </div>

    <div class="video-card">
      <img src="/stream.mjpg" alt="Flux caméra">
    </div>

    <section class="panel">
      <div class="controls">
        <div class="empty"></div>
        <button onclick="move('up')">↑</button>
        <div class="empty"></div>

        <button onclick="move('left')">←</button>
        <button class="center" onclick="move('center')">CENTRE</button>
        <button onclick="move('right')">→</button>

        <div class="empty"></div>
        <button onclick="move('down')">↓</button>
        <div class="empty"></div>
      </div>

      <div class="status" id="status">
        PAN: {{ pan }}° — TILT: {{ tilt }}°
      </div>

      <div class="small">
        Centre calibré : PAN {{ pan_center }}° / TILT {{ tilt_center }}°
      </div>
    </section>
  </main>

  <script>
    async function move(direction) {
      try {
        const res = await fetch(`/api/move/${direction}`, { method: "POST" });
        const data = await res.json();

        document.getElementById("status").textContent =
          `PAN: ${data.pan}° — TILT: ${data.tilt}°`;
      } catch (err) {
        document.getElementById("status").textContent =
          "Erreur de contrôle servo";
        console.error(err);
      }
    }

    document.addEventListener("keydown", (event) => {
      const key = event.key.toLowerCase();

      if (key === "arrowup" || key === "w") move("up");
      if (key === "arrowdown" || key === "s") move("down");
      if (key === "arrowleft" || key === "a") move("left");
      if (key === "arrowright" || key === "d") move("right");
      if (key === "c") move("center");
    });
  </script>
</body>
</html>
"""


# =========================
# CAMERA STREAM
# =========================

app = Flask(__name__)


class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = threading.Condition()

    def write(self, buf):
        with self.condition:
            self.frame = bytes(buf)
            self.condition.notify_all()
        return len(buf)


picam2 = Picamera2()

camera_config = picam2.create_video_configuration(
    main={"size": (WIDTH, HEIGHT)},
    controls={"FrameRate": FPS}
)

picam2.configure(camera_config)

output = StreamingOutput()


@app.route("/")
def index():
    return render_template_string(
        PAGE,
        pan=pan,
        tilt=tilt,
        pan_center=PAN_CENTER,
        tilt_center=TILT_CENTER,
    )


@app.route("/api/move/<direction>", methods=["POST"])
def api_move(direction):
    if direction not in ["left", "right", "up", "down", "center"]:
        return jsonify({"error": "direction invalide"}), 400

    move_servo(direction)

    return jsonify({
        "pan": pan,
        "tilt": tilt,
        "pan_center": PAN_CENTER,
        "tilt_center": TILT_CENTER,
    })


def generate_stream():
    while True:
        with output.condition:
            output.condition.wait()
            frame = output.frame

        if frame:
            yield (
                b"--FRAME\r\n"
                b"Content-Type: image/jpeg\r\n"
                b"Content-Length: " + str(len(frame)).encode() + b"\r\n\r\n" +
                frame +
                b"\r\n"
            )


@app.route("/stream.mjpg")
def stream():
    return Response(
        generate_stream(),
        mimetype="multipart/x-mixed-replace; boundary=FRAME"
    )


if __name__ == "__main__":
    print("======================================")
    print("Raspberry Pi Caméra Motorisée")
    print(f"Config: {CONFIG_PATH}")
    print(f"PAN channel: {PAN_CH} | center: {PAN_CENTER} | invert: {INVERT_PAN}")
    print(f"TILT channel: {TILT_CH} | center: {TILT_CENTER} | invert: {INVERT_TILT}")
    print(f"URL: http://0.0.0.0:{PORT}")
    print("======================================")

    picam2.start_recording(
        MJPEGEncoder(bitrate=8000000),
        FileOutput(output)
    )

    try:
        app.run(host="0.0.0.0", port=PORT, threaded=True)
    finally:
        picam2.stop_recording()
