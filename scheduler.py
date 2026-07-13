# Scheduler - Sistema de notificacoes e agendamentos
import threading
import time
import json
import os
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

SUBSCRIPTIONS_FILE = os.path.join(DATA_DIR, "subscriptions.json")
NOTIFICATIONS_FILE = os.path.join(DATA_DIR, "notifications.json")
SCHEDULE_FILE = os.path.join(DATA_DIR, "schedule.json")
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
                self._check_subscriptions()
                self._check_schedule()
                self._check_campaigns()
                self._send_pending()
            except Exception as e:
                print(f"[Scheduler] Erro: {e}", flush=True)
            time.sleep(60)
    
    def _check_subscriptions(self):
        subs = load_json(SUBSCRIPTIONS_FILE, [])
        now = datetime.now()
        
        for sub in subs:
            if sub.get("notified"):
                continue
            
            end_date = datetime.fromisoformat(sub["end_date"])
            days_left = (end_date - now).days
            
            if days_left <= 0:
                msg = f"Olá {sub.get('name', '')}! Sua assinatura do BarberFlow ({sub.get('plan', '')}) expirou. Acesse barber-flow.store/auth para renovar."
                self._queue_notification(sub["phone"], msg, "expired")
                sub["notified"] = True
                sub["status"] = "expired"
            elif days_left <= 3:
                msg = f"Olá {sub.get('name', '')}! Sua assinatura do BarberFlow expira em {days_left} dia(s). Plano: {sub.get('plan', '')} - R$ {sub.get('price', '')}. Renove em barber-flow.store/auth"
                self._queue_notification(sub["phone"], msg, "reminder_3d")
                sub["notified"] = True
            elif days_left <= 7:
                msg = f"Olá {sub.get('name', '')}! Sua assinatura do BarberFlow expira em {days_left} dias. Plano: {sub.get('plan', '')} - R$ {sub.get('price', '')}."
                self._queue_notification(sub["phone"], msg, "reminder_7d")
                sub["notified"] = True
        
        save_json(SUBSCRIPTIONS_FILE, subs)
    
    def _check_schedule(self):
        schedule = load_json(SCHEDULE_FILE, [])
        now = datetime.now()
        
        for appt in schedule:
            if appt.get("notified"):
                continue
            
            appt_time = datetime.fromisoformat(appt["datetime"])
            diff = (appt_time - now).total_seconds() / 60
            
            if diff <= 0 and not appt.get("notified"):
                msg = f"Olá {appt.get('client_name', '')}! Lembrete: seu horário na {appt.get('barbershop', '')} é HOJE às {appt_time.strftime('%H:%M')}. Confirme respondendo SIM."
                self._queue_notification(appt["phone"], msg, "appointment")
                appt["notified"] = True
            elif 55 <= diff <= 65:
                msg = f"Olá {appt.get('client_name', '')}! Seu horário na {appt.get('barbershop', '')} é amanhã às {appt_time.strftime('%H:%M')}. Confirme respondendo SIM."
                self._queue_notification(appt["phone"], msg, "tomorrow")
                appt["notified"] = True
        
        save_json(SCHEDULE_FILE, schedule)
    
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


class SubscriptionManager:
    def add(self, phone, name, plan, price, end_date):
        subs = load_json(SUBSCRIPTIONS_FILE, [])
        sub = {
            "id": len(subs) + 1,
            "phone": phone,
            "name": name,
            "plan": plan,
            "price": price,
            "end_date": end_date,
            "status": "active",
            "notified": False,
            "created_at": datetime.now().isoformat()
        }
        subs.append(sub)
        save_json(SUBSCRIPTIONS_FILE, subs)
        return sub
    
    def get_all(self):
        return load_json(SUBSCRIPTIONS_FILE, [])
    
    def get_active(self):
        subs = self.get_all()
        return [s for s in subs if s.get("status") == "active"]
    
    def update_status(self, sub_id, status):
        subs = self.get_all()
        for s in subs:
            if s["id"] == sub_id:
                s["status"] = status
                if status == "paid":
                    s["notified"] = False
                    s["end_date"] = (datetime.now() + timedelta(days=30)).isoformat()
                break
        save_json(SUBSCRIPTIONS_FILE, subs)
    
    def delete(self, sub_id):
        subs = self.get_all()
        subs = [s for s in subs if s["id"] != sub_id]
        save_json(SUBSCRIPTIONS_FILE, subs)


class ScheduleManager:
    def add(self, phone, client_name, barbershop, datetime_str, service=""):
        schedule = load_json(SCHEDULE_FILE, [])
        appt = {
            "id": len(schedule) + 1,
            "phone": phone,
            "client_name": client_name,
            "barbershop": barbershop,
            "datetime": datetime_str,
            "service": service,
            "status": "confirmed",
            "notified": False,
            "created_at": datetime.now().isoformat()
        }
        schedule.append(appt)
        save_json(SCHEDULE_FILE, schedule)
        return appt
    
    def get_all(self):
        return load_json(SCHEDULE_FILE, [])
    
    def get_by_date(self, date_str):
        schedule = self.get_all()
        return [s for s in schedule if s["datetime"].startswith(date_str)]
    
    def get_by_phone(self, phone):
        schedule = self.get_all()
        return [s for s in schedule if s["phone"] == phone]
    
    def cancel(self, appt_id):
        schedule = self.get_all()
        schedule = [s for s in schedule if s["id"] != appt_id]
        save_json(SCHEDULE_FILE, schedule)


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
        save_json(CAMPAIGNS_FILE, camp)
        return camp
    
    def get_all(self):
        return load_json(CAMPAIGNS_FILE, [])
    
    def delete(self, camp_id):
        campaigns = self.get_all()
        campaigns = [c for c in campaigns if c["id"] != camp_id]
        save_json(CAMPAIGNS_FILE, campaigns)


scheduler = NotificationManager()
subscriptions = SubscriptionManager()
schedule_mgr = ScheduleManager()
campaigns = CampaignManager()
