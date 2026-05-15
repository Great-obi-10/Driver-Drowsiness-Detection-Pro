# Driver Drowsiness Detection Pro 🚗💤

![License](https://img.shields.io/badge/License-MIT-green)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-orange)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Google-blue)

**A real-time AI-powered driver monitoring system** that detects fatigue and drowsiness using facial landmarks, eye closure, yawning, and head pose estimation.

---

## 🎯 Project Overview

**Driver Drowsiness Detection Pro** is an intelligent computer vision application designed to enhance road safety by monitoring driver alertness in real-time. The system analyzes facial features using **MediaPipe Face Mesh** and calculates a composite **Fatigue Score** to determine if the driver is in a **NORMAL**, **DROWSY**, or **DANGER** state.

Built with a modular and clean architecture, making it easy to extend and customize.

---

## ✨ Key Features

- **Real-time Eye Closure Detection** using Eye Aspect Ratio (EAR)
- **Yawn Detection** using Mouth Aspect Ratio (MAR)
- **Blink & Yawn Counter**
- **Head Pose Estimation** (Yaw, Pitch, Roll)
- **Microsleep Detection** via sudden head pitch drop
- **Composite Fatigue Scoring** (0–100)
- **Three-Level Alert System**: Normal → Drowsy → Danger
- **Audible Alarm** with pygame
- **Telegram Notifications** support
- **CSV Event Logging** for analysis
- **Clean, customizable configuration**

---

## 📸 Demo Screenshots

*(Add your screenshots here)*

![dashboard preview](screenshots/dashboard.png)
![telegram preview](screenshots/drowsy.png)

---

## 🛠️ Tech Stack

| Technology       | Purpose                        |
|------------------|--------------------------------|
| Python 3.11+     | Core language                  |
| OpenCV           | Video processing & visualization |
| MediaPipe        | Face landmark detection        |
| NumPy            | Numerical computations         |
| Pygame           | Alarm sound playback           |
| Requests         | Telegram API integration       |

---

## 📁 Project Structure

```bash
drowsiness-system/
├── main.py                 # Main application
├── config.py               # All settings and thresholds
├── fatigue_scorer.py       # EAR, MAR & fatigue scoring logic
├── head_pose.py            # Head pose estimation
├── alert_system.py         # Sound + Telegram alerts
├── logger.py               # CSV logging
├── requirements.txt
├── sounds/
│   └── alarm.wav
├── logs/
│   └── fatigue_events.csv
├── screenshots/
└── README.md
```

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/great-obi-10/driver-drowsiness-detection.git
cd driver-drowsiness-detection-pro
```

### 2. Create Virtual Environment (Recommended)

```bash
# Using Python 3.11
python -m venv venv
venv\Scripts\activate     # Windows
# source venv/bin/activate # macOS/Linux
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🎮 How to Run

```bash
python main.py
```

**Controls:**
- Press **`q`** to quit the application

---

## ⚙️ Configuration (`config.py`)

You can easily customize the system by modifying `config.py`:

```python
# Thresholds
EAR_THRESHOLD = 0.22
MAR_THRESHOLD = 0.65
YAW_DISTRACTION_THRESHOLD = 25.0
DANGER_THRESHOLD = 60

# Alerts
ENABLE_SOUND = True
ENABLE_TELEGRAM = False
ALARM_SOUND = "sounds/alarm.wav"
```

**Telegram Setup:**
1. Create a bot with [@BotFather](https://t.me/botfather)
2. Set `ENABLE_TELEGRAM = True`
3. Add your `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`

---

## 📊 How It Works

1. Captures video from webcam
2. Detects 468 facial landmarks using MediaPipe
3. Calculates:
   - Eye Aspect Ratio (EAR)
   - Mouth Aspect Ratio (MAR)
   - Head orientation (Yaw, Pitch, Roll)
4. Computes real-time **Fatigue Score**
5. Triggers visual + audio alerts when needed

---

## 🎵 Alarm Sound

Place any `.wav` alarm sound file in the `sounds/` folder and name it `alarm.wav`.

---

## 📈 Future Enhancements

- [ ] Add face recognition (known driver)
- [ ] Mobile app integration
- [ ] drowsiness prediction using ML model
- [ ] Support for multiple cameras
- [ ] GUI with settings panel
- [ ] Cloud logging & dashboard

---

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. Fork the project
2. Create your feature branch
3. Submit a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Great Obi**  
Built with ❤️ for road safety

---
