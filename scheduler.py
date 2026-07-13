# Scheduler - Notificacoes e Campanhas
import threading
import time
import json
import os
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

NOTIFICATIONS_FILE = os.path.join(DATA_DIR, "notifications.json")
CAMPAIGNS_FILE = os.path.join(DATA_DIR, "campaigns.json")

def load_json(path, default=None):
    if default is None:
        default = {}
    if os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except:
            return default
    return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


class NotificationManager:
    def __init__(self):
        self.send_callback = None
        self.running = False
        self._thread = None
    
    def set_sender(self, callback):
        self.send_callback = callback
    
    def send(self, phone, message):
        if self.send_callback:
            return self.send_callback(phone, message)
        return False
    
    def start(self):
        self.running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
    
    def stop(self):
        self.running = False
    
    def _loop(self):
        while self.running:
            try:
                self._check_campaigns()
                self._send_pending()
            except Exception as e:
                print(f"[Scheduler] Erro: {e}", flush=True)
            time.sleep(60)
    
    def _check_campaigns(self):
        campaigns = load_json(CAMPAIGNS_FILE, [])
        now = datetime.now()
        
        for camp in campaigns:
            if camp.get("sent"):
                continue
            
            send_at = datetime.fromisoformat(camp["send_at"])
            if now >= send_at:
                for phone in camp.get("recipients", []):
                    self._queue_notification(phone, camp["message"], "campaign")
                camp["sent"] = True
        
        save_json(CAMPAIGNS_FILE, campaigns)
    
    def _queue_notification(self, phone, message, type):
        notifs = load_json(NOTIFICATIONS_FILE, [])
        notifs.append({
            "phone": phone,
            "message": message,
            "type": type,
            "timestamp": datetime.now().isoformat(),
            "sent": False
        })
        save_json(NOTIFICATIONS_FILE, notifs)
    
    def _send_pending(self):
        notifs = load_json(NOTIFICATIONS_FILE, [])
        changed = False
        
        for notif in notifs:
            if not notif.get("sent"):
                success = self.send(notif["phone"], notif["message"])
                if success:
                    notif["sent"] = True
                    notif["sent_at"] = datetime.now().isoformat()
                    changed = True
        
        if changed:
            save_json(NOTIFICATIONS_FILE, notifs)
    
    def get_pending(self):
        notifs = load_json(NOTIFICATIONS_FILE, [])
        return [n for n in notifs if not n.get("sent")]
    
    def get_sent(self):
        notifs = load_json(NOTIFICATIONS_FILE, [])
        return [n for n in notifs if n.get("sent")]
    
    def queue(self, phone, message, type="manual"):
        self._queue_notification(phone, message, type)


class CampaignManager:
    def add(self, name, message, recipients, send_at):
        campaigns = load_json(CAMPAIGNS_FILE, [])
        camp = {
            "id": len(campaigns) + 1,
            "name": name,
            "message": message,
            "recipients": recipients,
            "send_at": send_at,
            "sent": False,
            "created_at": datetime.now().isoformat()
        }
        campaigns.append(camp)
        save_json(CAMPAIGNS_FILE, campaigns)
        return camp
    
    def get_all(self):
        return load_json(CAMPAIGNS_FILE, [])
    
    def delete(self, camp_id):
        campaigns = self.get_all()
        campaigns = [c for c in campaigns if c["id"] != camp_id]
        save_json(CAMPAIGNS_FILE, campaigns)


scheduler = NotificationManager()
campaigns = CampaignManager()
