"""
main.py — Driver Drowsiness Detection Pro
Upgraded with Web Dashboard + Improved Sudden Head Drop Detection
"""

import cv2
import mediapipe as mp
import sys
import os

import config as cfg
from fatigue_scorer import FatigueScorer, compute_ear, compute_mar
from head_pose import HeadPoseEstimator
from alert_system import AlertSystem
from logger import EventLogger

# Dashboard integration
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dashboard'))
from app import start_dashboard, update_state, update_frame, add_event

# MediaPipe landmark indices
LEFT_EYE  = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]
MOUTH     = [61, 81, 13, 311, 291, 402, 14, 178]

mp_face_mesh = mp.solutions.face_mesh


def extract_points(landmarks, indices, w, h):
    return [(int(landmarks[i].x * w), int(landmarks[i].y * h)) for i in indices]


def draw_poly(frame, points, color, thickness=1):
    """Thin lines for maximum eye visibility"""
    for i in range(len(points)):
        cv2.line(frame, points[i], points[(i + 1) % len(points)], color, thickness)
    
    # Very small dots on eye landmarks
    for point in points:
        cv2.circle(frame, point, 1, (255, 255, 255), -1)


def draw_hud(frame, metrics, yaw, pitch, roll, pitch_drop, sudden_drop, status):
    """Draw all HUD text overlays on the frame."""
    h, w = frame.shape[:2]

    status_colors = {
        "NORMAL": cfg.GREEN,
        "DROWSY": cfg.YELLOW,
        "DANGER": cfg.RED,
    }
    color = status_colors.get(status, cfg.WHITE)

    cv2.rectangle(frame, (0, 0), (w, 36), (0, 0, 0), -1)
    cv2.putText(frame, f"Status: {status}",
                (w // 2 - 80, 26),
                cv2.FONT_HERSHEY_SIMPLEX, 0.85, color, 2)

    lines = [
        (f"EAR: {metrics.get('ear', 0):.3f}",           cfg.YELLOW),
        (f"Closed Frames: {metrics['closed_frames']}",   cfg.CYAN),
        (f"Blinks: {metrics['blinks']}",                 cfg.WHITE),
        ("",                                             cfg.WHITE),
        (f"MAR: {metrics.get('mar', 0):.3f}",            cfg.MAGENTA),
        (f"Yawn Frames: {metrics['yawn_frames']}",       cfg.YELLOW),
        (f"Yawns: {metrics['yawns']}",                   cfg.WHITE),
        ("",                                             cfg.WHITE),
        (f"Yaw Angle: {yaw:.1f}°",                       cfg.WHITE),
        ("FOCUS FORWARD" if abs(yaw) < cfg.YAW_DISTRACTION_THRESHOLD
         else "LOOKING AWAY",
         cfg.GREEN if abs(yaw) < cfg.YAW_DISTRACTION_THRESHOLD else cfg.RED),
        ("",                                             cfg.WHITE),
        (f"Pitch: {pitch:.1f}°" +
         (" ⚠ HEAD DROP" if pitch_drop else ""),
         cfg.RED if pitch_drop else cfg.WHITE),
        ("",                                             cfg.WHITE),
        (f"Fatigue Score: {metrics['fatigue_score']}",   color),
    ]

    y = 60
    for text, col in lines:
        if text:
            cv2.putText(frame, text, (20, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.68, col, 2)
        y += 26

    if sudden_drop:
        cv2.rectangle(frame, (0, h - 70), (w, h), (0, 0, 220), -1)
        cv2.putText(frame, "🚨 SUDDEN HEAD DROP DETECTED!",
                    (w // 2 - 220, h - 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.85, cfg.WHITE, 3)
        cv2.putText(frame, "MICROSLEEP / DROWSINESS ALERT!",
                    (w // 2 - 180, h - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, cfg.WHITE, 2)

    cv2.putText(frame, "Press 'q' to quit", (20, h - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, cfg.WHITE, 1)

    return frame


def main():
    print("\n" + "="*60)
    print("     DRIVER DROWSINESS DETECTION PRO")
    print("          with Sudden Head Drop Detection")
    print("="*60)

    start_dashboard(host="0.0.0.0", port=cfg.DASHBOARD_PORT)

    cap = cv2.VideoCapture(cfg.CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  cfg.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg.FRAME_HEIGHT)

    scorer    = FatigueScorer()
    head_pose = HeadPoseEstimator()
    alerts    = AlertSystem(cfg)
    logger    = EventLogger(cfg.LOG_FILE)

    last_logged_status = "NORMAL"
    head_drops = 0

    with mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as face_mesh:

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb)

            metrics = {"fatigue_score": 0, "status": "NORMAL",
                       "closed_frames": 0, "blinks": 0,
                       "yawn_frames": 0, "yawns": 0,
                       "ear": 0.0, "mar": 0.0}

            yaw = pitch = roll = 0.0
            pitch_drop = sudden_drop = False

            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0].landmark

                left_eye  = extract_points(landmarks, LEFT_EYE,  w, h)
                right_eye = extract_points(landmarks, RIGHT_EYE, w, h)
                mouth     = extract_points(landmarks, MOUTH,     w, h)

                ear = (compute_ear(left_eye) + compute_ear(right_eye)) / 2.0
                mar = compute_mar(mouth)

                yaw, pitch, roll, pitch_drop, sudden_drop = head_pose.estimate(landmarks, w, h)

                if sudden_drop or pitch_drop:
                    head_drops += 1

                metrics = scorer.update(ear, mar, yaw, pitch_drop, roll, sudden_drop, cfg)
                metrics["ear"] = ear
                metrics["mar"] = mar

                status = metrics["status"]

                # ================== THIN EYE LINES ==================
                draw_poly(frame, left_eye,  (0, 255, 255), thickness=1)   # Cyan Left Eye
                draw_poly(frame, right_eye, (0, 165, 255), thickness=1)   # Orange Right Eye
                draw_poly(frame, mouth,     cfg.BLUE, thickness=2)

                # Alerts & Logging
                if status == "DANGER":
                    alerts.play_alarm()
                    if last_logged_status != "DANGER":
                        alerts.send_telegram(
                            f"🚨 DANGER! Sudden Head Drop + Fatigue Score: {metrics['fatigue_score']}"
                        )
                        add_event("DANGER", metrics['fatigue_score'], "Sudden head drop detected")
                else:
                    alerts.stop_alarm()

                if status != last_logged_status:
                    logger.log(status, metrics['fatigue_score'], ear, mar, yaw, pitch, roll)
                    last_logged_status = status

            frame = draw_hud(frame, metrics, yaw, pitch, roll, pitch_drop, sudden_drop, metrics["status"])

            _, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            update_frame(jpeg.tobytes())

            update_state(
                ear=metrics.get("ear", 0),
                mar=metrics.get("mar", 0),
                yaw=yaw,
                pitch=pitch,
                roll=roll,
                blinks=metrics["blinks"],
                yawns=metrics["yawns"],
                head_drops=head_drops,
                closed_frames=metrics["closed_frames"],
                fatigue_score=metrics["fatigue_score"],
                status=metrics["status"],
                focus="FOCUS FORWARD" if abs(yaw) < cfg.YAW_DISTRACTION_THRESHOLD else "LOOKING AWAY"
            )

            cv2.imshow(cfg.WINDOW_NAME, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    alerts.stop_alarm()
    cap.release()
    cv2.destroyAllWindows()
    print("\nSession ended.")


if __name__ == "__main__":
    main()