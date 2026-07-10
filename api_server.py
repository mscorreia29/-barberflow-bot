# WhatsApp Bot BarberFlow - API Server
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify, send_file
from bot import bot
from config import BOT_NAME
import os

app = Flask(__name__)
QR_FILE = os.path.join(os.path.dirname(__file__), 'whatsapp-bridge', 'qrcode.png')

@app.route('/', methods=['GET'])
def root():
    """Pagina inicial"""
    return jsonify({"message": "BarberFlow Bot API", "status": "running", "endpoints": ["/health", "/chat", "/stats", "/qr"]})

@app.route('/qr', methods=['GET'])
def qr_code():
    """Exibir QR Code para conectar WhatsApp"""
    if os.path.exists(QR_FILE):
        return send_file(QR_FILE, mimetype='image/png')
    return jsonify({"error": "QR Code ainda nao gerado. Aguarde..."}), 404

@app.route('/health', methods=['GET'])
def health():
    """Verificar se a API esta rodando"""
    return jsonify({"status": "ok", "bot": BOT_NAME})

@app.route('/chat', methods=['POST'])
def chat():
    """Processar mensagem e retornar resposta"""
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
        
        return jsonify({
            "response": response,
            "phone": phone,
            "processed": True
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stats', methods=['GET'])
def stats():
    """Obter estatisticas do bot"""
    stats = bot.get_stats()
    return jsonify(stats)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"Iniciando API do {BOT_NAME}...")
    print(f"API rodando em http://0.0.0.0:{port}")
    print(f"Health check: http://0.0.0.0:{port}/health")
    print("Aguardando conexoes...\n")
    app.run(host='0.0.0.0', port=port, debug=False)
