import subprocess
import sys
import os
import threading
import time

bridge_status = {"running": False, "pid": None, "exit_code": None}

def start_bridge():
    global bridge_status
    time.sleep(3)
    print("[API] Starting WhatsApp Bridge...", flush=True)
    try:
        log_file = open("/app/bridge.log", "w")
        proc = subprocess.Popen(
            ["node", "index.js"],
            cwd="/app/whatsapp-bridge",
            stdout=log_file,
            stderr=subprocess.STDOUT
        )
        bridge_status = {"running": True, "pid": proc.pid, "exit_code": None}
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
from flask import Flask, request, jsonify, send_file
from bot import bot
from config import BOT_NAME

app = Flask(__name__)
QR_FILE = '/app/whatsapp-bridge/qrcode.png'

@app.route('/')
def root():
    return jsonify({"status": "running", "bot": BOT_NAME, "endpoints": ["/health", "/chat", "/stats", "/qr"]})

@app.route('/health')
def health():
    return jsonify({"status": "ok", "bot": BOT_NAME})

@app.route('/qr')
def qr_code():
    if os.path.exists(QR_FILE):
        return send_file(QR_FILE, mimetype='image/png')
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
    log = ""
    try:
        with open("/app/bridge.log") as f:
            log = f.read()[-2000:]
    except:
        pass
    s["bridge_log"] = log
    return jsonify(s)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"[API] {BOT_NAME} em http://0.0.0.0:{port}", flush=True)
    app.run(host='0.0.0.0', port=port, debug=False)
