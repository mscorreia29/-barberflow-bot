# Multi-Tenant System - AutoAssist
import json
import os
import secrets
import hashlib
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
TENANTS_DIR = os.path.join(DATA_DIR, "tenants")
ADMIN_FILE = os.path.join(DATA_DIR, "admin.json")

os.makedirs(TENANTS_DIR, exist_ok=True)

def load_json(path, default=None):
    if default is None: default = {}
    if os.path.exists(path):
        try:
            with open(path) as f: return json.load(f)
        except: return default
    return default

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f: json.dump(data, f, indent=2, ensure_ascii=False)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_id():
    return secrets.token_hex(8)


DEFAULT_KNOWLEDGE = {
    "bot_name": "",
    "business_name": "",
    "business_type": "geral",
    "support_hours": "Seg-Sex 9h-18h",
    "phone": "",
    "website": "",
    "greeting": "Ola! Sou o assistente virtual. Como posso te ajudar?",
    "responses": {}
}

DEFAULT_CONFIG = {
    "whatsapp_phone": "",
    "groq_api_key": "",
    "ai_model": "llama-3.3-70b-versatile",
    "max_tokens": 200,
    "ignore_groups": True,
    "theme_color": "#00d4aa"
}


class TenantManager:
    def __init__(self):
        self._ensure_admin()
    
    def _ensure_admin(self):
        admin = load_json(ADMIN_FILE, None)
        if not admin:
            admin = {
                "email": "admin@autoassist.com",
                "password": hash_password("aa2026!"),
                "created_at": datetime.now().isoformat()
            }
            save_json(ADMIN_FILE, admin)
    
    def _tenant_dir(self, tenant_id):
        d = os.path.join(TENANTS_DIR, tenant_id)
        os.makedirs(d, exist_ok=True)
        os.makedirs(os.path.join(d, "data"), exist_ok=True)
        return d
    
    def _tenant_file(self, tenant_id, filename):
        return os.path.join(self._tenant_dir(tenant_id), filename)
    
    def create(self, name, email, password, business_name="", business_type="geral"):
        tenants = self.get_all()
        
        for t in tenants:
            if t["email"] == email:
                return None, "Email ja cadastrado"
        
        tenant_id = generate_id()
        tenant = {
            "id": tenant_id,
            "name": name,
            "email": email,
            "password": hash_password(password),
            "business_name": business_name or name,
            "business_type": business_type,
            "plan": "free",
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        tenants.append(tenant)
        save_json(os.path.join(DATA_DIR, "tenants.json"), tenants)
        
        knowledge = DEFAULT_KNOWLEDGE.copy()
        knowledge["bot_name"] = name
        knowledge["business_name"] = business_name or name
        knowledge["business_type"] = business_type
        save_json(self._tenant_file(tenant_id, "knowledge.json"), knowledge)
        
        config = DEFAULT_CONFIG.copy()
        save_json(self._tenant_file(tenant_id, "config.json"), config)
        
        save_json(self._tenant_file(tenant_id, "data/conversations.json"), {})
        save_json(self._tenant_file(tenant_id, "data/contacts.json"), [])
        save_json(self._tenant_file(tenant_id, "data/templates.json"), [])
        save_json(self._tenant_file(tenant_id, "data/analytics.json"), {"messages": [], "response_times": []})
        save_json(self._tenant_file(tenant_id, "data/campaigns.json"), [])
        save_json(self._tenant_file(tenant_id, "data/notifications.json"), [])
        
        return tenant, None
    
    def authenticate(self, email, password):
        tenants = self.get_all()
        for t in tenants:
            if t["email"] == email and t["password"] == hash_password(password):
                return t
        return None
    
    def authenticate_admin(self, email, password):
        admin = load_json(ADMIN_FILE)
        if admin and admin["email"] == email and admin["password"] == hash_password(password):
            return True
        return False
    
    def get_all(self):
        return load_json(os.path.join(DATA_DIR, "tenants.json"), [])
    
    def get_by_id(self, tenant_id):
        tenants = self.get_all()
        return next((t for t in tenants if t["id"] == tenant_id), None)
    
    def get_by_email(self, email):
        tenants = self.get_all()
        return next((t for t in tenants if t["email"] == email), None)
    
    def update(self, tenant_id, **kwargs):
        tenants = self.get_all()
        for t in tenants:
            if t["id"] == tenant_id:
                for k, v in kwargs.items():
                    if k != "id" and k != "created_at":
                        t[k] = v
                t["updated_at"] = datetime.now().isoformat()
                save_json(os.path.join(DATA_DIR, "tenants.json"), tenants)
                return t
        return None
    
    def delete(self, tenant_id):
        tenants = self.get_all()
        tenants = [t for t in tenants if t["id"] != tenant_id]
        save_json(os.path.join(DATA_DIR, "tenants.json"), tenants)
        
        tenant_dir = os.path.join(TENANTS_DIR, tenant_id)
        if os.path.exists(tenant_dir):
            import shutil
            shutil.rmtree(tenant_dir)
    
    def get_knowledge(self, tenant_id):
        return load_json(self._tenant_file(tenant_id, "knowledge.json"), DEFAULT_KNOWLEDGE)
    
    def save_knowledge(self, tenant_id, knowledge):
        save_json(self._tenant_file(tenant_id, "knowledge.json"), knowledge)
    
    def get_config(self, tenant_id):
        return load_json(self._tenant_file(tenant_id, "config.json"), DEFAULT_CONFIG)
    
    def save_config(self, tenant_id, config):
        save_json(self._tenant_file(tenant_id, "config.json"), config)
    
    def get_data(self, tenant_id, filename):
        return load_json(self._tenant_file(tenant_id, f"data/{filename}"), [])
    
    def save_data(self, tenant_id, filename, data):
        save_json(self._tenant_file(tenant_id, f"data/{filename}"), data)
    
    def get_stats(self, tenant_id):
        conversations = self.get_data(tenant_id, "conversations.json")
        contacts_list = self.get_data(tenant_id, "contacts.json")
        templates_list = self.get_data(tenant_id, "templates.json")
        analytics_data = self.get_data(tenant_id, "analytics.json")
        
        return {
            "total_conversations": len(conversations) if isinstance(conversations, dict) else 0,
            "total_contacts": len(contacts_list) if isinstance(contacts_list, list) else 0,
            "total_templates": len(templates_list) if isinstance(templates_list, list) else 0,
            "total_messages": len(analytics_data.get("messages", [])) if isinstance(analytics_data, dict) else 0
        }
    
    def list_tenants_summary(self):
        tenants = self.get_all()
        summary = []
        for t in tenants:
            stats = self.get_stats(t["id"])
            summary.append({
                **t,
                "password": "***",
                "stats": stats
            })
        return summary


tenants = TenantManager()
