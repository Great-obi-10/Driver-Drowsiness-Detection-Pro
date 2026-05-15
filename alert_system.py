"""Sound and Telegram alerts with cooldown."""

import os
import threading
import time
import config as cfg


class AlertSystem:
    def __init__(self, cfg):
        self.cfg = cfg
        self.alarm_playing = False
        self.last_alarm_time = 0
        self.ALARM_COOLDOWN = 8   # seconds between alarms

        if cfg.ENABLE_SOUND:
            try:
                import pygame
                pygame.mixer.init()
                if os.path.exists(cfg.ALARM_SOUND):
                    self.sound = pygame.mixer.Sound(cfg.ALARM_SOUND)
                else:
                    self.sound = None
            except Exception:
                self.sound = None
        else:
            self.sound = None

    def play_alarm(self):
        """Play alarm only if cooldown has passed"""
        current_time = time.time()
        
        if (self.sound and 
            not self.alarm_playing and 
            (current_time - self.last_alarm_time) > self.ALARM_COOLDOWN):
            
            self.sound.play(-1)  # loop
            self.alarm_playing = True
            self.last_alarm_time = current_time

    def stop_alarm(self):
        if self.sound and self.alarm_playing:
            self.sound.stop()
            self.alarm_playing = False

    def send_telegram(self, message):
        if not self.cfg.ENABLE_TELEGRAM:
            return
        if not self.cfg.TELEGRAM_BOT_TOKEN or not self.cfg.TELEGRAM_CHAT_ID:
            return

        def _send():
            try:
                url = f"https://api.telegram.org/bot{self.cfg.TELEGRAM_BOT_TOKEN}/sendMessage"
                requests.post(
                    url,
                    data={"chat_id": self.cfg.TELEGRAM_CHAT_ID, "text": message},
                    timeout=5,
                )
            except Exception:
                pass

        threading.Thread(target=_send, daemon=True).start()