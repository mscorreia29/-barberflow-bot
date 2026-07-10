# WhatsApp Bot BarberFlow - API Server
import sys
import os
import subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify, send_file
from bot import bot
from config import BOT_NAME

app = Flask(__name__)

QR_FILE = '/app/whatsapp-bridge/qrcode.png'

@app.route('/', methods=['GET'])
def root():
    return jsonify({"message": "BarberFlow Bot API", "status": "running", "endpoints": ["/health", "/chat", "/stats", "/qr", "/debug"]})

@app.route('/qr', methods=['GET'])
def qr_code():
    if os.path.exists(QR_FILE):
        return send_file(QR_FILE, mimetype='image/png')
    return jsonify({"error": "QR Code ainda nao gerado. Aguarde...", "path_checked": QR_FILE, "exists": os.path.exists(QR_FILE)}), 404

@app.route('/logs', methods=['GET'])
def logs():
    try:
        with open('/app/bridge.log', 'r') as f:
            content = f.read()
        return content, 200, {'Content-Type': 'text/plain'}
    except:
        return jsonify({"error": "bridge.log nao existe ainda"}), 404

@app.route('/debug', methods=['GET'])
def debug():
    port = os.environ.get('PORT', 'not set')
    node_running = False
    try:
        result = subprocess.run(['pgrep', '-f', 'node index.js'], capture_output=True, text=True)
        node_running = result.returncode == 0
    except:
        pass

    qr_exists = os.path.exists(QR_FILE)
    qr_size = os.path.getsize(QR_FILE) if qr_exists else 0

    auth_exists = os.path.exists('/app/whatsapp-bridge/auth_state')

    return jsonify({
        "port": port,
        "node_bridge_running": node_running,
        "qr_file_exists": qr_exists,
        "qr_file_size": qr_size,
        "auth_state_exists": auth_exists,
        "bot_api_url": f"http://127.0.0.1:{port}"
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "bot": BOT_NAME})

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
            return jsonify({"error": "phone e message sao obrigatorios"}), 400

        response = bot.handle_message(phone, message, is_group)
        return jsonify({"response": response, "phone": phone, "processed": True})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stats', methods=['GET'])
def stats():
    return jsonify(bot.get_stats())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Iniciando API do {BOT_NAME}...")
    print(f"API rodando em http://0.0.0.0:{port}")
    print(f"PORT env: {os.environ.get('PORT', 'not set')}")
    app.run(host='0.0.0.0', port=port, debug=False)
