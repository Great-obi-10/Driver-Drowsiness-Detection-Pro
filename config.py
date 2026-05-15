"""Configuration settings for Driver Drowsiness Detection Pro."""

# Webcam
CAMERA_INDEX = 0
WINDOW_NAME  = "Driver Drowsiness Detection Pro"
FRAME_WIDTH  = 640
FRAME_HEIGHT = 480

# Eye thresholds — more sensitive
EAR_THRESHOLD      = 0.25   # was 0.22 — easier to trigger
EAR_CONSEC_FRAMES  = 10     # was 15 — faster response

# Mouth thresholds
MAR_THRESHOLD      = 0.55   # was 0.65 — easier to detect yawn
MAR_CONSEC_FRAMES  = 10     # was 15

# Head pose — more sensitive
YAW_DISTRACTION_THRESHOLD = 15.0   # was 25 — triggers sooner
ROLL_FATIGUE_THRESHOLD    = 15.0   # was 20
PITCH_DROP_THRESHOLD      = 10.0   # was 15

# Status thresholds — lower so DROWSY/DANGER trigger faster
DROWSY_THRESHOLD = 20    # was 30
DANGER_THRESHOLD = 40    # was 60


# Alerts
ALARM_SOUND    = "sounds/alarm.wav"
ENABLE_SOUND   = True
ENABLE_TELEGRAM = True

# Telegram
TELEGRAM_BOT_TOKEN = "8282658706:AAGCat-rwVqYFCMNeBxLTmiQjiMQ3CsaxrY"
TELEGRAM_CHAT_ID   = "6252607378"

# Logging
LOG_FILE = "logs/fatigue_events.csv"

# Dashboard
DASHBOARD_PORT = 5000

# Colors (BGR)
WHITE  = (255, 255, 255)
GREEN  = (0, 255, 0)
RED    = (0, 0, 255)
YELLOW = (0, 255, 255)
CYAN   = (255, 255, 0)
MAGENTA = (255, 0, 255)
BLUE   = (255, 0, 0)
MUTED  = (100, 100, 100)

DROWSY_THRESHOLD = 35
DANGER_THRESHOLD = 40        # Increased so alarm doesn't trigger too easily

# Make sudden drop still strong, but not instant alarm
YAW_DISTRACTION_THRESHOLD = 22
PITCH_DROP_THRESHOLD = 20