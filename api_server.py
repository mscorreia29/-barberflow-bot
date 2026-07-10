# WhatsApp Bot BarberFlow - API Server
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify, send_file
from bot import bot
from config import BOT_NAME

app = Flask(__name__)

QR_PATHS = [
    '/app/whatsapp_bridge_qr.png',
    os.path.join(os.path.dirname(__file__), 'whatsapp-bridge', 'qrcode.png'),
    os.path.join(os.path.dirname(__file__), 'whatsapp_bridge_qr.png'),
]

@app.route('/', methods=['GET'])
def root():
    return jsonify({"message": "BarberFlow Bot API", "status": "running", "endpoints": ["/health", "/chat", "/stats", "/qr", "/debug"]})

@app.route('/qr', methods=['GET'])
def qr_code():
    for p in QR_PATHS:
        if os.path.exists(p):
            return send_file(p, mimetype='image/png')
    return jsonify({"error": "QR Code ainda nao gerado. Aguarde...", "checked_paths": QR_PATHS}), 404

@app.route('/debug', methods=['GET'])
def debug():
    files = []
    for root_dir, dirs, fnames in os.walk('/app'):
        for f in fnames:
            if f.endswith('.png') or f.endswith('.json'):
                files.append(os.path.join(root_dir, f))
    return jsonify({"files": files, "port": os.environ.get('PORT', 'not set')})

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
    print(f"Health check: http://0.0.0.0:{port}/health")
    print("Aguardando conexoes...\n")
    app.run(host='0.0.0.0', port=port, debug=False)
