import subprocess
import sys
import os
import threading
import time
import secrets
from datetime import datetime
from functools import wraps

bridge_status = {"running": False, "pid": None, "exit_code": None, "started_at": None}

def start_bridge():
    global bridge_status
    time.sleep(3)
    print(f"[API] Starting WhatsApp Bridge... {datetime.now()}", flush=True)
    try:
        log_file = open("/app/bridge.log", "w")
        proc = subprocess.Popen(
            ["node", "index.js"],
            cwd="/app/whatsapp-bridge",
            stdout=log_file,
            stderr=subprocess.STDOUT
        )
        bridge_status = {"running": True, "pid": proc.pid, "exit_code": None, "started_at": str(datetime.now())}
        print(f"[API] Bridge started PID={proc.pid}", flush=True)
        proc.wait()
        bridge_status["running"] = False
        bridge_status["exit_code"] = proc.returncode
        print(f"[API] Bridge exited code={proc.returncode}. Restarting in 5s...", flush=True)
        time.sleep(5)
        start_bridge()
    except Exception as e:
        bridge_status["running"] = False
        print(f"[API] Bridge error: {e}", flush=True)
        time.sleep(5)
        start_bridge()

t = threading.Thread(target=start_bridge, daemon=True)
t.start()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from flask import Flask, request, jsonify, send_file, send_from_directory, session, redirect, url_for
from tenants import tenants, DATA_DIR, load_json, save_json
from analytics import Analytics, ContactManager, TemplateManager

app = Flask(__name__, static_folder='static')
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("tenant_id") and not session.get("is_admin"):
            if request.is_json or request.path.startswith("/api/"):
                return jsonify({"error": "Nao autenticado"}), 401
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("is_admin"):
            if request.is_json or request.path.startswith("/api/"):
                return jsonify({"error": "Nao autorizado"}), 401
            return redirect(url_for("admin_login_page"))
        return f(*args, **kwargs)
    return decorated

def get_tenant_analytics(tid):
    data = tenants.get_data(tid, "analytics.json")
    return Analytics(data) if isinstance(data, dict) else Analytics()

def get_tenant_contacts(tid):
    data = tenants.get_data(tid, "contacts.json")
    return ContactManager(data) if isinstance(data, list) else ContactManager()

def get_tenant_templates(tid):
    data = tenants.get_data(tid, "templates.json")
    return TemplateManager(data) if isinstance(data, list) else TemplateManager()


# ==================== AUTH PAGES ====================

@app.route("/")
def root():
    if session.get("tenant_id"):
        return send_from_directory(app.static_folder, "tenant.html")
    if session.get("is_admin"):
        return send_from_directory(app.static_folder, "admin.html")
    return redirect(url_for("login_page"))

@app.route("/register", methods=["GET"])
def register_page():
    if session.get("tenant_id"):
        return redirect("/app")
    error = request.args.get("error")
    success = request.args.get("success")
    return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>AutoAssist - Cadastro</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Inter',-apple-system,sans-serif;background:#0b0e14;color:#e4e8f0;min-height:100vh;display:flex;align-items:center;justify-content:center}}
.card{{background:#1a1f2e;border:1px solid #252d3d;border-radius:16px;padding:40px;width:100%;max-width:440px;text-align:center}}
.card h1{{font-size:24px;margin-bottom:4px}} .card h1 span{{color:#00d4aa}} .card p{{color:#8892a4;font-size:14px;margin-bottom:24px}}
.card input,.card select{{width:100%;padding:12px 16px;border-radius:8px;border:1px solid #252d3d;background:#161b28;color:#e4e8f0;font-size:14px;outline:none;margin-bottom:12px;font-family:inherit}}
.card input:focus,.card select:focus{{border-color:#00d4aa}}
.card button{{width:100%;padding:12px;border-radius:8px;border:none;background:#00d4aa;color:#000;font-size:14px;font-weight:700;cursor:pointer;margin-top:4px}}
.card button:hover{{background:#00b894}}
.error{{background:#ff475722;color:#ff4757;padding:10px;border-radius:8px;font-size:13px;margin-bottom:16px}}
.success{{background:#00d4aa22;color:#00d4aa;padding:10px;border-radius:8px;font-size:13px;margin-bottom:16px}}
.link{{color:#00d4aa;font-size:13px;margin-top:16px;display:block}}
.row{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}
</style></head><body>
<div class="card">
<h1><span>Auto</span>Assist</h1>
<p>Crie sua conta gratuita</p>
{"<div class='error'>"+error+"</div>" if error else ""}
{"<div class='success'>"+success+"</div>" if success else ""}
<form method="POST" action="/register">
<div class="row">
<input type="text" name="name" placeholder="Seu nome" required>
<input type="text" name="business_name" placeholder="Nome do negocio" required>
</div>
<input type="email" name="email" placeholder="Email" required>
<input type="password" name="password" placeholder="Senha (min 6 caracteres)" required minlength="6">
<select name="business_type">
<option value="barbearia">Barbearia</option><option value="salao">Salao de beleza</option>
<option value="clinica">Clinica</option><option value="academia">Academia</option>
<option value="restaurante">Restaurante</option><option value="loja">Loja</option>
<option value="servicos">Servicos</option><option value="geral">Outro</option>
</select>
<button type="submit">Criar Conta</button>
</form>
<a class="link" href="/login">Ja tenho conta? Entrar</a>
</div></body></html>'''

@app.route("/register", methods=["POST"])
def register_post():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    business_name = request.form.get("business_name", "").strip()
    business_type = request.form.get("business_type", "geral")
    
    if len(password) < 6:
        return redirect("/register?error=Senha+minima+de+6+caracteres")
    
    tenant, error = tenants.create(name, email, password, business_name, business_type)
    if error:
        return redirect(f"/register?error={error}")
    
    return redirect("/login?success=Conta+criada!+Faca+login.")

@app.route("/login", methods=["GET"])
def login_page():
    if session.get("tenant_id"):
        return redirect("/app")
    error = request.args.get("error")
    success = request.args.get("success")
    return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>AutoAssist - Login</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Inter',-apple-system,sans-serif;background:#0b0e14;color:#e4e8f0;min-height:100vh;display:flex;align-items:center;justify-content:center}}
.card{{background:#1a1f2e;border:1px solid #252d3d;border-radius:16px;padding:40px;width:100%;max-width:400px;text-align:center}}
.card h1{{font-size:24px;margin-bottom:4px}} .card h1 span{{color:#00d4aa}} .card p{{color:#8892a4;font-size:14px;margin-bottom:32px}}
.card input{{width:100%;padding:12px 16px;border-radius:8px;border:1px solid #252d3d;background:#161b28;color:#e4e8f0;font-size:14px;outline:none;margin-bottom:12px;font-family:inherit}}
.card input:focus{{border-color:#00d4aa}}
.card button{{width:100%;padding:12px;border-radius:8px;border:none;background:#00d4aa;color:#000;font-size:14px;font-weight:700;cursor:pointer;margin-top:4px}}
.card button:hover{{background:#00b894}}
.error{{background:#ff475722;color:#ff4757;padding:10px;border-radius:8px;font-size:13px;margin-bottom:16px}}
.success{{background:#00d4aa22;color:#00d4aa;padding:10px;border-radius:8px;font-size:13px;margin-bottom:16px}}
.link{{color:#00d4aa;font-size:13px;margin-top:16px;display:block}}
</style></head><body>
<div class="card">
<h1><span>Auto</span>Assist</h1>
<p>Painel de Controle</p>
{"<div class='error'>"+error+"</div>" if error else ""}
{"<div class='success'>"+success+"</div>" if success else ""}
<form method="POST" action="/login">
<input type="email" name="email" placeholder="Email" required>
<input type="password" name="password" placeholder="Senha" required>
<button type="submit">Entrar</button>
</form>
<a class="link" href="/register">Nao tenho conta? Criar</a>
<a class="link" href="/admin/login" style="color:#8892a4">Admin</a>
</div></body></html>'''

@app.route("/login", methods=["POST"])
def login_post():
    email = request.form.get("email", "")
    password = request.form.get("password", "")
    
    if tenants.authenticate_admin(email, password):
        session["is_admin"] = True
        session["admin_email"] = email
        return redirect("/dashboard")
    
    tenant = tenants.authenticate(email, password)
    if tenant:
        session["tenant_id"] = tenant["id"]
        session["tenant_name"] = tenant["name"]
        session["tenant_email"] = tenant["email"]
        return redirect("/app")
    return redirect("/login?error=Credenciais+invalidas")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ==================== ADMIN AUTH ====================

@app.route("/admin/login", methods=["GET"])
def admin_login_page():
    if session.get("is_admin"):
        return redirect("/admin")
    error = request.args.get("error")
    return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>AutoAssist - Admin Login</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Inter',-apple-system,sans-serif;background:#0b0e14;color:#e4e8f0;min-height:100vh;display:flex;align-items:center;justify-content:center}}
.card{{background:#1a1f2e;border:1px solid #252d3d;border-radius:16px;padding:40px;width:100%;max-width:400px;text-align:center}}
.card h1{{font-size:20px;margin-bottom:4px;color:#ff4757}} .card p{{color:#8892a4;font-size:14px;margin-bottom:32px}}
.card input{{width:100%;padding:12px 16px;border-radius:8px;border:1px solid #252d3d;background:#161b28;color:#e4e8f0;font-size:14px;outline:none;margin-bottom:12px;font-family:inherit}}
.card input:focus{{border-color:#ff4757}}
.card button{{width:100%;padding:12px;border-radius:8px;border:none;background:#ff4757;color:#fff;font-size:14px;font-weight:700;cursor:pointer;margin-top:4px}}
.error{{background:#ff475722;color:#ff4757;padding:10px;border-radius:8px;font-size:13px;margin-bottom:16px}}
.link{{color:#8892a4;font-size:13px;margin-top:16px;display:block}}
</style></head><body>
<div class="card">
<h1>Admin Panel</h1>
<p>Gerenciamento de tenants</p>
{"<div class='error'>"+error+"</div>" if error else ""}
<form method="POST" action="/admin/login">
<input type="email" name="email" placeholder="Email admin" required>
<input type="password" name="password" placeholder="Senha" required>
<button type="submit">Entrar</button>
</form>
<a class="link" href="/login">Voltar ao login</a>
</div></body></html>'''

@app.route("/admin/login", methods=["POST"])
def admin_login_post():
    email = request.form.get("email", "")
    password = request.form.get("password", "")
    if tenants.authenticate_admin(email, password):
        session["is_admin"] = True
        session["admin_email"] = email
        return redirect("/admin")
    return redirect("/admin/login?error=Credenciais+invalidas")

@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    session.pop("admin_email", None)
    return redirect("/admin/login")


# ==================== TENANT DASHBOARD ====================

@app.route("/app")
@login_required
def tenant_dashboard():
    return send_file(os.path.join(app.static_folder, "tenant.html"))

@app.route("/health")
def health():
    return jsonify({"status": "ok", "bridge_running": bridge_status.get("running", False)})

@app.route("/api/auth/me")
@login_required
def auth_me():
    tid = session["tenant_id"]
    t = tenants.get_by_id(tid)
    if not t:
        return jsonify({"error": "Tenant nao encontrado"}), 404
    t["password"] = "***"
    return jsonify(t)

@app.route("/api/knowledge", methods=["GET"])
@login_required
def get_knowledge():
    return jsonify(tenants.get_knowledge(session["tenant_id"]))

@app.route("/api/knowledge", methods=["POST"])
@login_required
def save_knowledge():
    data = request.get_json()
    tenants.save_knowledge(session["tenant_id"], data)
    return jsonify({"ok": True})

@app.route("/api/tenant/config", methods=["GET"])
@login_required
def get_tenant_config():
    return jsonify(tenants.get_config(session["tenant_id"]))

@app.route("/api/tenant/config", methods=["POST"])
@login_required
def save_tenant_config():
    data = request.get_json()
    tenants.save_config(session["tenant_id"], data)
    return jsonify({"ok": True})

@app.route("/api/tenant/stats")
@login_required
def tenant_stats():
    tid = session["tenant_id"]
    return jsonify(tenants.get_stats(tid))

@app.route("/api/contacts", methods=["GET"])
@login_required
def get_contacts():
    cm = get_tenant_contacts(session["tenant_id"])
    return jsonify(cm.get_all())

@app.route("/api/contacts", methods=["POST"])
@login_required
def add_contact():
    data = request.get_json()
    cm = get_tenant_contacts(session["tenant_id"])
    c = cm.add(phone=data["phone"], name=data.get("name", ""), tags=data.get("tags", []), notes=data.get("notes", ""))
    tenants.save_data(session["tenant_id"], "contacts.json", cm.contacts)
    return jsonify(c)

@app.route("/api/contacts/<int:cid>", methods=["PUT"])
@login_required
def update_contact(cid):
    data = request.get_json()
    cm = get_tenant_contacts(session["tenant_id"])
    c = cm.update(cid, **data)
    tenants.save_data(session["tenant_id"], "contacts.json", cm.contacts)
    return jsonify(c or {"error": "not found"})

@app.route("/api/contacts/<int:cid>", methods=["DELETE"])
@login_required
def delete_contact(cid):
    cm = get_tenant_contacts(session["tenant_id"])
    cm.delete(cid)
    tenants.save_data(session["tenant_id"], "contacts.json", cm.contacts)
    return jsonify({"ok": True})

@app.route("/api/templates", methods=["GET"])
@login_required
def get_templates():
    tm = get_tenant_templates(session["tenant_id"])
    return jsonify(tm.get_all())

@app.route("/api/templates", methods=["POST"])
@login_required
def add_template():
    data = request.get_json()
    tm = get_tenant_templates(session["tenant_id"])
    t = tm.add(name=data["name"], content=data["content"], category=data.get("category", "geral"))
    tenants.save_data(session["tenant_id"], "templates.json", tm.templates)
    return jsonify(t)

@app.route("/api/templates/<int:tid>", methods=["DELETE"])
@login_required
def delete_template(tid):
    tm = get_tenant_templates(session["tenant_id"])
    tm.delete(tid)
    tenants.save_data(session["tenant_id"], "templates.json", tm.templates)
    return jsonify({"ok": True})

@app.route("/api/send", methods=["POST"])
@login_required
def api_send():
    data = request.get_json()
    phone = data.get("phone", "")
    message = data.get("message", "")
    if not phone or not message:
        return jsonify({"error": "phone e message obrigatorios"}), 400
    try:
        import requests as req
        resp = req.post(f"http://127.0.0.1:{os.environ.get('PORT', 5000)}/chat",
                       json={"phone": phone, "message": message, "is_group": False})
        return jsonify({"ok": resp.ok})
    except:
        return jsonify({"ok": False})

@app.route("/api/export/contacts")
@login_required
def export_contacts():
    import csv, io
    cm = get_tenant_contacts(session["tenant_id"])
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Nome", "Telefone", "Tags", "Notas", "Criado em"])
    for c in cm.get_all():
        writer.writerow([c.get("name", ""), c.get("phone", ""), ",".join(c.get("tags", [])), c.get("notes", ""), c.get("created_at", "")])
    from flask import Response
    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=contatos.csv"})


# ==================== ADMIN DASHBOARD ====================

@app.route("/admin")
@admin_required
def admin_dashboard():
    return send_file(os.path.join(app.static_folder, "admin.html"))

@app.route("/admin/api/tenants", methods=["GET"])
@admin_required
def admin_list_tenants():
    return jsonify(tenants.list_tenants_summary())

@app.route("/admin/api/tenants", methods=["POST"])
@admin_required
def admin_create_tenant():
    data = request.get_json()
    t, error = tenants.create(
        name=data["name"], email=data["email"], password=data["password"],
        business_name=data.get("business_name", ""), business_type=data.get("business_type", "geral")
    )
    if error:
        return jsonify({"error": error}), 400
    t["password"] = "***"
    return jsonify(t)

@app.route("/admin/api/tenants/<tid>", methods=["PUT"])
@admin_required
def admin_update_tenant(tid):
    data = request.get_json()
    t = tenants.update(tid, **data)
    if t:
        t["password"] = "***"
    return jsonify(t or {"error": "not found"})

@app.route("/admin/api/tenants/<tid>", methods=["DELETE"])
@admin_required
def admin_delete_tenant(tid):
    tenants.delete(tid)
    return jsonify({"ok": True})

@app.route("/admin/api/tenants/<tid>/stats", methods=["GET"])
@admin_required
def admin_tenant_stats(tid):
    return jsonify(tenants.get_stats(tid))


# ==================== ADMIN TEMPLATES ====================

ADMIN_TEMPLATES_FILE = os.path.join(DATA_DIR, "admin_templates.json")

def load_admin_templates():
    return load_json(ADMIN_TEMPLATES_FILE, [])

def save_admin_templates(data):
    save_json(ADMIN_TEMPLATES_FILE, data)

@app.route("/admin/api/templates", methods=["GET"])
@admin_required
def admin_get_templates():
    return jsonify(load_admin_templates())

@app.route("/admin/api/templates", methods=["POST"])
@admin_required
def admin_add_template():
    data = request.get_json()
    tmpls = load_admin_templates()
    tmpl = {
        "id": len(tmpls) + 1,
        "name": data["name"],
        "content": data["content"],
        "category": data.get("category", "geral"),
        "created_at": datetime.now().isoformat()
    }
    tmpls.append(tmpl)
    save_admin_templates(tmpls)
    return jsonify(tmpl)

@app.route("/admin/api/templates/<int:tid>", methods=["PUT"])
@admin_required
def admin_update_template(tid):
    data = request.get_json()
    tmpls = load_admin_templates()
    for t in tmpls:
        if t["id"] == tid:
            t["name"] = data.get("name", t["name"])
            t["content"] = data.get("content", t["content"])
            t["category"] = data.get("category", t["category"])
            save_admin_templates(tmpls)
            return jsonify(t)
    return jsonify({"error": "not found"}), 404

@app.route("/admin/api/templates/<int:tid>", methods=["DELETE"])
@admin_required
def admin_delete_template(tid):
    tmpls = load_admin_templates()
    tmpls = [t for t in tmpls if t["id"] != tid]
    save_admin_templates(tmpls)
    return jsonify({"ok": True})


# ==================== HEALTH (PUBLIC) ====================

@app.route("/qr")
def qr_code():
    qr = '/app/whatsapp-bridge/qrcode.png'
    if os.path.exists(qr):
        return send_file(qr, mimetype='image/png')
    return jsonify({"error": "QR Code ainda nao gerado"}), 404


# ==================== OWNER DASHBOARD (ORIGINAL) ====================

from bot import bot
from config import BOT_NAME as ORIGINAL_BOT_NAME
from scheduler import scheduler, campaigns
from analytics import Analytics as GlobalAnalytics, ContactManager as GlobalContacts, TemplateManager as GlobalTemplates

global_analytics = GlobalAnalytics()
global_contacts = GlobalContacts()
global_templates = GlobalTemplates()

@app.route("/dashboard")
@login_required
def owner_dashboard():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/dashboard/health")
@login_required
def owner_health():
    return jsonify({"status": "ok", "bot": ORIGINAL_BOT_NAME, "bridge_running": bridge_status.get("running", False)})

@app.route("/dashboard/stats")
@login_required
def owner_stats():
    s = bot.get_stats()
    s["bridge"] = bridge_status
    s["conversations"] = {}
    for phone, msgs in bot.conversations.items():
        s["conversations"][phone] = [{"role": m["role"], "content": m["content"]} for m in msgs]
    s["pending_notifications"] = scheduler.get_pending()
    s["campaigns"] = campaigns.get_all()
    s["analytics"] = {
        "daily": global_analytics.get_daily_stats(7),
        "avg_response_time": global_analytics.get_avg_response_time(),
        "total_messages": global_analytics.get_total_messages(),
        "hourly": global_analytics.get_hourly_distribution()
    }
    s["contacts"] = global_contacts.get_all()
    s["templates"] = global_templates.get_all()
    s["total_contacts"] = len(global_contacts.get_all())
    try:
        with open("/app/bridge.log") as f:
            s["bridge_log"] = f.read()[-2000:]
    except:
        s["bridge_log"] = ""
    return jsonify(s)

@app.route("/dashboard/conversations/<phone>")
@login_required
def owner_conversation(phone):
    if phone in bot.conversations:
        return jsonify(bot.conversations[phone])
    return jsonify([])

@app.route("/dashboard/chat", methods=["POST"])
@login_required
def owner_chat():
    try:
        data = request.get_json()
        phone = data.get("phone", "")
        message = data.get("message", "")
        is_group = data.get("is_group", False)
        if not phone or not message:
            return jsonify({"error": "phone e message obrigatorios"}), 400
        analytics.log_message(phone, "inbound")
        start = datetime.now()
        response = bot.handle_message(phone, message, is_group)
        elapsed = (datetime.now() - start).total_seconds()
        analytics.log_response_time(phone, elapsed)
        analytics.log_message(phone, "outbound")
        global_contacts.update_last_message(phone)
        return jsonify({"response": response, "phone": phone, "processed": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/dashboard/send", methods=["POST"])
@login_required
def owner_send():
    data = request.get_json()
    phone = data.get("phone", "")
    message = data.get("message", "")
    if not phone or not message:
        return jsonify({"error": "phone e message obrigatorios"}), 400
    try:
        import requests as req
        resp = req.post(f"http://127.0.0.1:{os.environ.get('PORT', 5000)}/chat",
                       json={"phone": phone, "message": message, "is_group": False})
        return jsonify({"ok": resp.ok})
    except:
        return jsonify({"ok": False})

@app.route("/dashboard/contacts", methods=["GET"])
@login_required
def owner_get_contacts():
    return jsonify(global_contacts.get_all())

@app.route("/dashboard/contacts", methods=["POST"])
@login_required
def owner_add_contact():
    data = request.get_json()
    c = global_contacts.add(phone=data["phone"], name=data.get("name", ""), tags=data.get("tags", []), notes=data.get("notes", ""))
    return jsonify(c)

@app.route("/dashboard/contacts/<int:cid>", methods=["DELETE"])
@login_required
def owner_delete_contact(cid):
    global_contacts.delete(cid)
    return jsonify({"ok": True})

@app.route("/dashboard/templates", methods=["GET"])
@login_required
def owner_get_templates():
    return jsonify(global_templates.get_all())

@app.route("/dashboard/templates", methods=["POST"])
@login_required
def owner_add_template():
    data = request.get_json()
    t = global_templates.add(name=data["name"], content=data["content"], category=data.get("category", "geral"))
    return jsonify(t)

@app.route("/dashboard/templates/<int:tid>", methods=["DELETE"])
@login_required
def owner_delete_template(tid):
    global_templates.delete(tid)
    return jsonify({"ok": True})

@app.route("/dashboard/campaigns", methods=["GET"])
@login_required
def owner_get_campaigns():
    return jsonify(campaigns.get_all())

@app.route("/dashboard/campaigns", methods=["POST"])
@login_required
def owner_add_campaign():
    data = request.get_json()
    camp = campaigns.add(name=data.get("name", "Campanha"), message=data["message"], recipients=data.get("recipients", []), send_at=data["send_at"])
    return jsonify(camp)

@app.route("/dashboard/campaigns/<int:camp_id>", methods=["DELETE"])
@login_required
def owner_delete_campaign(camp_id):
    campaigns.delete(camp_id)
    return jsonify({"ok": True})

@app.route("/dashboard/notifications/pending")
@login_required
def owner_pending():
    return jsonify(scheduler.get_pending())

@app.route("/dashboard/notifications/sent")
@login_required
def owner_sent():
    return jsonify(scheduler.get_sent())

@app.route("/dashboard/export/contacts")
@login_required
def owner_export_contacts():
    import csv, io
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Nome", "Telefone", "Tags", "Notas", "Criado em"])
    for c in global_contacts.get_all():
        writer.writerow([c.get("name", ""), c.get("phone", ""), ",".join(c.get("tags", [])), c.get("notes", ""), c.get("created_at", "")])
    from flask import Response
    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=contatos.csv"})

@app.route("/dashboard/export/conversations")
@login_required
def owner_export_conversations():
    import csv, io
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Telefone", "Papel", "Mensagem", "Timestamp"])
    for phone, msgs in bot.conversations.items():
        for m in msgs:
            writer.writerow([phone, m["role"], m["content"], ""])
    from flask import Response
    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=conversas.csv"})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"[API] AutoAssist Multi-Tenant em http://0.0.0.0:{port}", flush=True)
    print(f"[API] Admin: admin@autoassist.com / admin123", flush=True)
    print(f"[API] Dashboard: /dashboard", flush=True)
    app.run(host='0.0.0.0', port=port, debug=False)
