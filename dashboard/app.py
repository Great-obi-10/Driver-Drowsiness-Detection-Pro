# =============================================================================
# dashboard/app.py — Flask Backend
# Streams live video + metrics to the web dashboard
# =============================================================================

from flask import Flask, Response, render_template, jsonify
import threading
import time
import json
import csv
import os
import sys

# Add parent directory to path so we can import project modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)

# Shared state between the detection thread and Flask
_state = {
    "frame":         None,         # latest JPEG frame bytes
    "ear":           0.0,
    "mar":           0.0,
    "yaw":           0.0,
    "pitch":         0.0,
    "roll":          0.0,
    "blinks":        0,
    "yawns":         0,
    "head_drops":    0,
    "closed_frames": 0,
    "fatigue_score": 0,
    "status":        "NORMAL",
    "focus":         "FOCUS FORWARD",
    "events":        [],           # last 20 alert events
    "history":       [],           # fatigue score history (last 60 points)
    "running":       False,
}
_lock = threading.Lock()


# -----------------------------------------------------------------------------
# STATE UPDATER (called from main.py)
# -----------------------------------------------------------------------------

def update_state(**kwargs):
    with _lock:
        for k, v in kwargs.items():
            if k in _state:
                _state[k] = v

        # Maintain history (last 60 score points)
        if "fatigue_score" in kwargs:
            _state["history"].append({
                "time":  time.strftime("%H:%M:%S"),
                "score": kwargs["fatigue_score"],
            })
            if len(_state["history"]) > 60:
                _state["history"].pop(0)


def update_frame(jpeg_bytes: bytes):
    with _lock:
        _state["frame"] = jpeg_bytes


def add_event(status: str, score: int, message: str = ""):
    with _lock:
        _state["events"].insert(0, {
            "time":    time.strftime("%H:%M:%S"),
            "status":  status,
            "score":   score,
            "message": message,
        })
        if len(_state["events"]) > 20:
            _state["events"].pop()


# -----------------------------------------------------------------------------
# ROUTES
# -----------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    """MJPEG stream for live camera feed."""
    return Response(
        _generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/metrics")
def metrics():
    """JSON endpoint for live metrics — polled by dashboard JS."""
    with _lock:
        return jsonify({
            "ear":           round(_state["ear"], 3),
            "mar":           round(_state["mar"], 3),
            "yaw":           round(_state["yaw"], 1),
            "pitch":         round(_state["pitch"], 1),
            "roll":          round(_state["roll"], 1),
            "blinks":        _state["blinks"],
            "yawns":         _state["yawns"],
            "head_drops":    _state["head_drops"],
            "closed_frames": _state["closed_frames"],
            "fatigue_score": _state["fatigue_score"],
            "status":        _state["status"],
            "focus":         _state["focus"],
            "events":        _state["events"][:10],
            "history":       _state["history"],
        })


@app.route("/logs")
def logs():
    """Return CSV log as JSON for the dashboard."""
    log_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "logs", "fatigue_events.csv"
    )
    rows = []
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)[-50:]  # last 50 events
    return jsonify(rows)


# -----------------------------------------------------------------------------
# MJPEG GENERATOR
# -----------------------------------------------------------------------------

def _generate_frames():
    while True:
        with _lock:
            frame = _state["frame"]

        if frame is not None:
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
            )
        time.sleep(0.03)  # ~30fps


# -----------------------------------------------------------------------------
# START DASHBOARD IN BACKGROUND THREAD
# -----------------------------------------------------------------------------

def start_dashboard(host="0.0.0.0", port=5000):
    """Start Flask in a background daemon thread."""
    def run():
        app.run(host=host, port=port, debug=False, use_reloader=False)

    t = threading.Thread(target=run, daemon=True)
    t.start()
    print(f"\n🌐 Dashboard running at: http://localhost:{port}\n")
    return t