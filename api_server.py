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
from bot import bot
from config import BOT_NAME
from scheduler import scheduler, campaigns
from analytics import analytics, contacts, templates

app = Flask(__name__, static_folder='static')
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

DASHBOARD_USER = os.environ.get("DASHBOARD_USER", "admin")
DASHBOARD_PASS = os.environ.get("DASHBOARD_PASS", "barberflow2024")

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("authenticated"):
            if request.is_json or request.path.startswith("/api/"):
                return jsonify({"error": "Nao autenticado"}), 401
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return decorated

@app.route("/login", methods=["GET"])
def login_page():
    if session.get("authenticated"):
        return redirect("/")
    error = request.args.get("error")
    return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AutoAssist - Login</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>💈</text></svg>">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0b0e14;color:#e4e8f0;min-height:100vh;display:flex;align-items:center;justify-content:center}}
.login-card{{background:#1a1f2e;border:1px solid #252d3d;border-radius:16px;padding:40px;width:100%;max-width:400px;text-align:center}}
.login-card h1{{font-size:24px;margin-bottom:4px}}
.login-card h1 span{{color:#00d4aa}}
.login-card p{{color:#8892a4;font-size:14px;margin-bottom:32px}}
.login-card input{{width:100%;padding:12px 16px;border-radius:8px;border:1px solid #252d3d;background:#161b28;color:#e4e8f0;font-size:14px;outline:none;margin-bottom:12px;font-family:inherit}}
.login-card input:focus{{border-color:#00d4aa}}
.login-card button{{width:100%;padding:12px;border-radius:8px;border:none;background:#00d4aa;color:#000;font-size:14px;font-weight:700;cursor:pointer;margin-top:4px}}
.login-card button:hover{{background:#00b894}}
.error{{background:#ff475722;color:#ff4757;padding:10px;border-radius:8px;font-size:13px;margin-bottom:16px}}
.icon{{font-size:48px;margin-bottom:16px}}
</style>
</head>
<body>
<div class="login-card">
<div class="icon">⚡</div>
<h1><span>Auto</span>Assist</h1>
<p>Painel de Controle</p>
{"<div class='error'>Credenciais invalidas</div>" if error else ""}
<form method="POST" action="/login">
<input type="text" name="username" placeholder="Usuario" required autofocus>
<input type="password" name="password" placeholder="Senha" required>
<button type="submit">Entrar</button>
</form>
</div>
</body>
</html>'''

@app.route("/login", methods=["POST"])
def login_post():
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    if username == DASHBOARD_USER and password == DASHBOARD_PASS:
        session["authenticated"] = True
        session["user"] = username
        return redirect("/")
    return redirect("/login?error=1")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route('/')
@login_required
def root():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/health')
def health():
    return jsonify({"status": "ok", "bot": BOT_NAME, "bridge_running": bridge_status.get("running", False)})

@app.route('/qr')
@login_required
def qr_code():
    qr = '/app/whatsapp-bridge/qrcode.png'
    if os.path.exists(qr):
        return send_file(qr, mimetype='image/png')
    return jsonify({"error": "QR Code ainda nao gerado"}), 404

@app.route('/chat', methods=['POST'])
@login_required
def chat():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Dados nao fornecidos"}), 400
        phone = data.get('phone', '')
        message = data.get('message', '')
        is_group = data.get('is_group', False)
        if not phone or not message:
            return jsonify({"error": "phone e message obrigatorios"}), 400

        analytics.log_message(phone, "inbound")
        start = datetime.now()
        response = bot.handle_message(phone, message, is_group)
        elapsed = (datetime.now() - start).total_seconds()
        analytics.log_response_time(phone, elapsed)
        analytics.log_message(phone, "outbound")
        contacts.update_last_message(phone)

        return jsonify({"response": response, "phone": phone, "processed": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stats')
@login_required
def stats():
    s = bot.get_stats()
    s["bridge"] = bridge_status
    s["conversations"] = {}
    for phone, msgs in bot.conversations.items():
        s["conversations"][phone] = [{"role": m["role"], "content": m["content"]} for m in msgs]
    s["pending_notifications"] = scheduler.get_pending()
    s["campaigns"] = campaigns.get_all()
    s["analytics"] = {
        "daily": analytics.get_daily_stats(7),
        "avg_response_time": analytics.get_avg_response_time(),
        "total_messages": analytics.get_total_messages(),
        "hourly": analytics.get_hourly_distribution()
    }
    s["contacts"] = contacts.get_all()
    s["templates"] = templates.get_all()
    s["total_contacts"] = len(contacts.get_all())
    try:
        with open("/app/bridge.log") as f:
            s["bridge_log"] = f.read()[-2000:]
    except:
        s["bridge_log"] = ""
    return jsonify(s)

@app.route('/conversations/<phone>')
@login_required
def get_conversation(phone):
    if phone in bot.conversations:
        return jsonify(bot.conversations[phone])
    return jsonify([])

# === SEND ===
@app.route('/api/send', methods=['POST'])
@login_required
def api_send():
    data = request.get_json()
    phone = data.get("phone", "")
    message = data.get("message", "")
    if not phone or not message:
        return jsonify({"error": "phone e message obrigatorios"}), 400
    success = bridge_send(phone, message)
    if success:
        analytics.log_message(phone, "outbound")
        scheduler.queue(phone, message, "manual")
    return jsonify({"ok": success})

# === CONTACTS ===
@app.route('/api/contacts', methods=['GET'])
@login_required
def get_contacts():
    return jsonify(contacts.get_all())

@app.route('/api/contacts', methods=['POST'])
@login_required
def add_contact():
    data = request.get_json()
    c = contacts.add(
        phone=data["phone"],
        name=data.get("name", ""),
        tags=data.get("tags", []),
        notes=data.get("notes", "")
    )
    return jsonify(c)

@app.route('/api/contacts/<int:cid>', methods=['PUT'])
@login_required
def update_contact(cid):
    data = request.get_json()
    c = contacts.update(cid, **data)
    return jsonify(c or {"error": "not found"})

@app.route('/api/contacts/<int:cid>', methods=['DELETE'])
@login_required
def delete_contact(cid):
    contacts.delete(cid)
    return jsonify({"ok": True})

@app.route('/api/contacts/<int:cid>/tags', methods=['POST'])
@login_required
def add_tag(cid):
    data = request.get_json()
    contacts.add_tag(cid, data["tag"])
    return jsonify({"ok": True})

@app.route('/api/contacts/<int:cid>/tags/<tag>', methods=['DELETE'])
@login_required
def remove_tag(cid, tag):
    contacts.remove_tag(cid, tag)
    return jsonify({"ok": True})

@app.route('/api/contacts/search')
@login_required
def search_contacts():
    q = request.args.get("q", "")
    return jsonify(contacts.search(q))

# === TEMPLATES ===
@app.route('/api/templates', methods=['GET'])
@login_required
def get_templates():
    return jsonify(templates.get_all())

@app.route('/api/templates', methods=['POST'])
@login_required
def add_template():
    data = request.get_json()
    t = templates.add(name=data["name"], content=data["content"], category=data.get("category", "geral"))
    return jsonify(t)

@app.route('/api/templates/<int:tid>', methods=['DELETE'])
@login_required
def delete_template(tid):
    templates.delete(tid)
    return jsonify({"ok": True})

# === CAMPAIGNS ===
@app.route('/api/campaigns', methods=['GET'])
@login_required
def get_campaigns():
    return jsonify(campaigns.get_all())

@app.route('/api/campaigns', methods=['POST'])
@login_required
def add_campaign():
    data = request.get_json()
    camp = campaigns.add(
        name=data.get("name", "Campanha"),
        message=data["message"],
        recipients=data.get("recipients", []),
        send_at=data["send_at"]
    )
    return jsonify(camp)

@app.route('/api/campaigns/<int:camp_id>', methods=['DELETE'])
@login_required
def delete_campaign(camp_id):
    campaigns.delete(camp_id)
    return jsonify({"ok": True})

# === NOTIFICATIONS ===
@app.route('/api/notifications/pending', methods=['GET'])
@login_required
def get_pending():
    return jsonify(scheduler.get_pending())

@app.route('/api/notifications/sent', methods=['GET'])
@login_required
def get_sent():
    return jsonify(scheduler.get_sent())

# === EXPORT ===
@app.route('/api/export/contacts')
@login_required
def export_contacts():
    import csv, io
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Nome", "Telefone", "Tags", "Notas", "Criado em"])
    for c in contacts.get_all():
        writer.writerow([c.get("name", ""), c.get("phone", ""), ",".join(c.get("tags", [])), c.get("notes", ""), c.get("created_at", "")])
    from flask import Response
    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=contatos.csv"})

@app.route('/api/export/conversations')
@login_required
def export_conversations():
    import csv, io
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Telefone", "Papel", "Mensagem", "Timestamp"])
    for phone, msgs in bot.conversations.items():
        for m in msgs:
            writer.writerow([phone, m["role"], m["content"], ""])
    from flask import Response
    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=conversas.csv"})

def bridge_send(phone, message):
    try:
        import requests as req
        resp = req.post(f"http://127.0.0.1:{os.environ.get('PORT', 5000)}/chat",
                       json={"phone": phone, "message": message, "is_group": False})
        return resp.ok
    except:
        return False

scheduler.set_sender(bridge_send)
scheduler.start()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"[API] {BOT_NAME} em http://0.0.0.0:{port}", flush=True)
    print(f"[API] Login: {DASHBOARD_USER}", flush=True)
    app.run(host='0.0.0.0', port=port, debug=False)
