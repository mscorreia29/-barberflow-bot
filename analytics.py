# Analytics - Metricas e contatos
import json
import os
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

ANALYTICS_FILE = os.path.join(DATA_DIR, "analytics.json")
CONTACTS_FILE = os.path.join(DATA_DIR, "contacts.json")
TEMPLATES_FILE = os.path.join(DATA_DIR, "templates.json")

def load_json(path, default=None):
    if default is None: default = {}
    if os.path.exists(path):
        try:
            with open(path) as f: return json.load(f)
        except: return default
    return default

def save_json(path, data):
    with open(path, "w") as f: json.dump(data, f, indent=2, ensure_ascii=False)


class Analytics:
    def __init__(self):
        self.data = load_json(ANALYTICS_FILE, {"messages": [], "response_times": []})
    
    def _save(self):
        save_json(ANALYTICS_FILE, self.data)
    
    def log_message(self, phone, direction, message_type="text"):
        self.data["messages"].append({
            "phone": phone,
            "direction": direction,
            "type": message_type,
            "timestamp": datetime.now().isoformat()
        })
        if len(self.data["messages"]) > 10000:
            self.data["messages"] = self.data["messages"][-5000:]
        self._save()
    
    def log_response_time(self, phone, seconds):
        self.data["response_times"].append({
            "phone": phone,
            "seconds": seconds,
            "timestamp": datetime.now().isoformat()
        })
        if len(self.data["response_times"]) > 5000:
            self.data["response_times"] = self.data["response_times"][-2500:]
        self._save()
    
    def get_daily_stats(self, days=7):
        now = datetime.now()
        stats = {}
        for i in range(days):
            date = (now - timedelta(days=i)).strftime("%Y-%m-%d")
            stats[date] = {"sent": 0, "received": 0}
        
        for msg in self.data["messages"]:
            date = msg["timestamp"][:10]
            if date in stats:
                if msg["direction"] == "outbound":
                    stats[date]["sent"] += 1
                else:
                    stats[date]["received"] += 1
        
        return stats
    
    def get_avg_response_time(self):
        times = self.data.get("response_times", [])
        if not times:
            return 0
        return round(sum(t["seconds"] for t in times) / len(times), 1)
    
    def get_total_messages(self):
        return len(self.data.get("messages", []))
    
    def get_hourly_distribution(self):
        hours = {str(h): 0 for h in range(24)}
        for msg in self.data.get("messages", []):
            h = msg["timestamp"][11:13]
            if h in hours:
                hours[h] += 1
        return hours


class ContactManager:
    def __init__(self):
        self.contacts = load_json(CONTACTS_FILE, [])
    
    def _save(self):
        save_json(CONTACTS_FILE, self.contacts)
    
    def add(self, phone, name="", tags=None, notes=""):
        existing = self.get_by_phone(phone)
        if existing:
            if name: existing["name"] = name
            if tags: existing["tags"] = list(set(existing.get("tags", []) + tags))
            if notes: existing["notes"] = notes
            self._save()
            return existing
        
        contact = {
            "id": len(self.contacts) + 1,
            "phone": phone,
            "name": name,
            "tags": tags or [],
            "notes": notes,
            "created_at": datetime.now().isoformat(),
            "last_message": None
        }
        self.contacts.append(contact)
        self._save()
        return contact
    
    def get_all(self):
        return self.contacts
    
    def get_by_phone(self, phone):
        return next((c for c in self.contacts if c["phone"] == phone), None)
    
    def get_by_tag(self, tag):
        return [c for c in self.contacts if tag in c.get("tags", [])]
    
    def update(self, contact_id, **kwargs):
        for c in self.contacts:
            if c["id"] == contact_id:
                for k, v in kwargs.items():
                    c[k] = v
                self._save()
                return c
        return None
    
    def delete(self, contact_id):
        self.contacts = [c for c in self.contacts if c["id"] != contact_id]
        self._save()
    
    def add_tag(self, contact_id, tag):
        for c in self.contacts:
            if c["id"] == contact_id:
                if tag not in c.get("tags", []):
                    c.setdefault("tags", []).append(tag)
                self._save()
                return c
        return None
    
    def remove_tag(self, contact_id, tag):
        for c in self.contacts:
            if c["id"] == contact_id:
                c["tags"] = [t for t in c.get("tags", []) if t != tag]
                self._save()
                return c
        return None
    
    def search(self, query):
        q = query.lower()
        return [c for c in self.contacts if q in c.get("name", "").lower() or q in c.get("phone", "")]
    
    def update_last_message(self, phone):
        c = self.get_by_phone(phone)
        if c:
            c["last_message"] = datetime.now().isoformat()
            self._save()
        else:
            self.add(phone, last_message=datetime.now().isoformat())


class TemplateManager:
    def __init__(self):
        self.templates = load_json(TEMPLATES_FILE, [])
    
    def _save(self):
        save_json(TEMPLATES_FILE, self.templates)
    
    def add(self, name, content, category="geral"):
        tmpl = {
            "id": len(self.templates) + 1,
            "name": name,
            "content": content,
            "category": category,
            "created_at": datetime.now().isoformat()
        }
        self.templates.append(tmpl)
        self._save()
        return tmpl
    
    def get_all(self):
        return self.templates
    
    def get_by_id(self, tmpl_id):
        return next((t for t in self.templates if t["id"] == tmpl_id), None)
    
    def delete(self, tmpl_id):
        self.templates = [t for t in self.templates if t["id"] != tmpl_id]
        self._save()


analytics = Analytics()
contacts = ContactManager()
templates = TemplateManager()
