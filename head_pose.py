"""Improved Head Pose Estimation with Sudden Head Drop Detection"""

class HeadPoseEstimator:
    def __init__(self):
        self.prev_pitch = 0.0
        self.pitch_history = []   # Track recent pitch values for sudden drop

    def estimate(self, landmarks, width, height):
        """Approximate head pose and detect both normal pitch drop + sudden head drop."""
        nose = landmarks[1]
        left_eye = landmarks[33]
        right_eye = landmarks[263]
        chin = landmarks[152]
        forehead = landmarks[10]

        # Convert normalized coordinates to pixels
        nx, ny = nose.x * width, nose.y * height
        lx, ly = left_eye.x * width, left_eye.y * height
        rx, ry = right_eye.x * width, right_eye.y * height
        cx, cy = chin.x * width, chin.y * height
        fx, fy = forehead.x * width, forehead.y * height

        # === Yaw (Left / Right head turn) ===
        eye_center_x = (lx + rx) / 2
        yaw = (nx - eye_center_x) * 1.2   # Increased sensitivity

        # === Pitch (Head Up / Down) ===
        face_height = max(cy - fy, 1)
        pitch = ((ny - fy) / face_height - 0.5) * 130   # More sensitive

        # === Roll ===
        roll = (ly - ry) * 0.35

        # === Sudden Head Drop Detection ===
        self.pitch_history.append(pitch)
        if len(self.pitch_history) > 12:          # Keep last 12 frames
            self.pitch_history.pop(0)

        sudden_drop = False
        if len(self.pitch_history) >= 5:
            # Check for big sudden downward movement
            recent_change = pitch - self.pitch_history[-5]
            if recent_change > 28 and pitch < -10:   # Strong downward spike
                sudden_drop = True

        # Regular pitch drop (for nodding/microsleep)
        pitch_drop = (pitch - self.prev_pitch) > 18 or sudden_drop

        self.prev_pitch = pitch

        return yaw, pitch, roll, pitch_drop, sudden_drop