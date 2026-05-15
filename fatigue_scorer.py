"""Fatigue scoring logic and EAR/MAR calculations."""

from math import hypot


def euclidean(p1, p2):
    """Calculate Euclidean distance between two points."""
    return hypot(p1[0] - p2[0], p1[1] - p2[1])


def compute_ear(eye_points):
    """Compute Eye Aspect Ratio from 6 eye landmark points."""
    if len(eye_points) != 6:
        return 0.0

    a = euclidean(eye_points[1], eye_points[5])
    b = euclidean(eye_points[2], eye_points[4])
    c = euclidean(eye_points[0], eye_points[3])

    if c == 0:
        return 0.0

    return (a + b) / (2.0 * c)


def compute_mar(mouth_points):
    """Compute Mouth Aspect Ratio from 8 mouth landmark points."""
    if len(mouth_points) != 8:
        return 0.0

    a = euclidean(mouth_points[1], mouth_points[7])
    b = euclidean(mouth_points[2], mouth_points[6])
    c = euclidean(mouth_points[3], mouth_points[5])
    d = euclidean(mouth_points[0], mouth_points[4])

    if d == 0:
        return 0.0

    return (a + b + c) / (3.0 * d)


class FatigueScorer:
    def __init__(self):
        self.closed_frames = 0
        self.yawn_frames = 0
        self.blinks = 0
        self.yawns = 0

    def update(self, ear, mar, yaw, pitch_drop, roll, sudden_drop, cfg):
        """
        Update fatigue score with sudden head drop detection.
        sudden_drop = Strong indicator of microsleep.
        """
        # Eye closure / blink detection
        if ear < cfg.EAR_THRESHOLD:
            self.closed_frames += 1
        else:
            if self.closed_frames >= 3:          # Slightly more stable
                self.blinks += 1
            self.closed_frames = 0

        # Yawning detection
        if mar > cfg.MAR_THRESHOLD:
            self.yawn_frames += 1
        else:
            if self.yawn_frames >= cfg.MAR_CONSEC_FRAMES:
                self.yawns += 1
            self.yawn_frames = 0

        # Score contributions
        eye_score = min(self.closed_frames * 2.5, 35)
        yawn_score = min(self.yawn_frames * 2.5, 20)
        
        yaw_score = 12 if abs(yaw) > cfg.YAW_DISTRACTION_THRESHOLD else 0
        roll_score = 10 if abs(roll) > cfg.ROLL_FATIGUE_THRESHOLD else 0
        pitch_score = 22 if pitch_drop else 0
        
        # HIGH WEIGHT for sudden head drop (very dangerous)
        sudden_drop_score = 45 if sudden_drop else 0

        blink_score = 8 if self.blinks > 18 else 0

        # Total fatigue score
        fatigue_score = (eye_score + yawn_score + yaw_score + 
                        pitch_score + roll_score + blink_score + sudden_drop_score)
        fatigue_score = min(fatigue_score, 100)

        # Determine status
        if fatigue_score >= cfg.DANGER_THRESHOLD:
            status = "DANGER"
        elif fatigue_score >= cfg.DROWSY_THRESHOLD:
            status = "DROWSY"
        else:
            status = "NORMAL"

        return {
            "fatigue_score": round(fatigue_score, 1),
            "status": status,
            "closed_frames": self.closed_frames,
            "blinks": self.blinks,
            "yawn_frames": self.yawn_frames,
            "yawns": self.yawns,
            "sudden_drop": sudden_drop,          # Added for dashboard
        }