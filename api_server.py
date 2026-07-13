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
from tenants import tenants
from analytics import Analytics, ContactManager, TemplateManager

app = Flask(__name__, static_folder='static')
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("tenant_id"):
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


# ==================== HEALTH (PUBLIC) ====================

@app.route("/qr")
def qr_code():
    qr = '/app/whatsapp-bridge/qrcode.png'
    if os.path.exists(qr):
        return send_file(qr, mimetype='image/png')
    return jsonify({"error": "QR Code ainda nao gerado"}), 404


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"[API] AutoAssist Multi-Tenant em http://0.0.0.0:{port}", flush=True)
    print(f"[API] Admin: admin@autoassist.com / admin123", flush=True)
    app.run(host='0.0.0.0', port=port, debug=False)
