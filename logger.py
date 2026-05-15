"""CSV event logging."""

import csv
import os
from datetime import datetime


class EventLogger:
    def __init__(self, file_path):
        self.file_path = file_path
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        if not os.path.exists(file_path):
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp", "status", "fatigue_score",
                    "ear", "mar", "yaw", "pitch", "roll"
                ])

    def log(self, status, score, ear, mar, yaw, pitch, roll):
        with open(self.file_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(timespec="seconds"),
                status,
                round(score, 1),
                round(ear, 3),
                round(mar, 3),
                round(yaw, 2),
                round(pitch, 2),
                round(roll, 2),
            ])