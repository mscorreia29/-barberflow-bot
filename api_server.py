import subprocess
import sys
import os
import threading
import time

def start_bridge():
    time.sleep(5)
    print("[API] Starting WhatsApp Bridge...", flush=True)
    try:
        proc = subprocess.Popen(
            ["node", "index.js"],
            cwd="/app/whatsapp-bridge",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        for line in proc.stdout:
            print(f"[Bridge] {line.decode('utf-8', errors='replace').strip()}", flush=True)
        print(f"[API] Bridge exited with code {proc.returncode}", flush=True)
    except Exception as e:
        print(f"[API] Bridge error: {e}", flush=True)

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
    return jsonify(bot.get_stats())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"[API] {BOT_NAME} em http://0.0.0.0:{port}", flush=True)
    app.run(host='0.0.0.0', port=port, debug=False)
