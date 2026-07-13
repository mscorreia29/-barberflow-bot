import subprocess
import sys
import os
import threading
import time
from datetime import datetime

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
from flask import Flask, request, jsonify, send_file, send_from_directory
from bot import bot
from config import BOT_NAME

app = Flask(__name__, static_folder='static')

@app.route('/')
def root():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/health')
def health():
    return jsonify({"status": "ok", "bot": BOT_NAME, "bridge_running": bridge_status.get("running", False)})

@app.route('/qr')
def qr_code():
    qr = '/app/whatsapp-bridge/qrcode.png'
    if os.path.exists(qr):
        return send_file(qr, mimetype='image/png')
    return jsonify({"error": "QR Code ainda nao gerado"}), 404

@app.route('/chat', methods=['POST'])
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
        response = bot.handle_message(phone, message, is_group)
        return jsonify({"response": response, "phone": phone, "processed": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stats')
def stats():
    s = bot.get_stats()
    s["bridge"] = bridge_status
    s["conversations"] = {}
    for phone, msgs in bot.conversations.items():
        s["conversations"][phone] = [{"role": m["role"], "content": m["content"]} for m in msgs]
    try:
        with open("/app/bridge.log") as f:
            s["bridge_log"] = f.read()[-2000:]
    except:
        s["bridge_log"] = ""
    return jsonify(s)

@app.route('/conversations/<phone>')
def get_conversation(phone):
    if phone in bot.conversations:
        return jsonify(bot.conversations[phone])
    return jsonify([])

@app.route('/send', methods=['POST'])
def send_message():
    return jsonify({"error": "Envio manual ainda nao implementado. Use o WhatsApp direto."}), 501

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"[API] {BOT_NAME} em http://0.0.0.0:{port}", flush=True)
    app.run(host='0.0.0.0', port=port, debug=False)
