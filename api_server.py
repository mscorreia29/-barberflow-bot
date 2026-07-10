from flask import Flask, request, jsonify, send_file
from bot import bot
from config import BOT_NAME
import os, glob

app = Flask(__name__)

QR_FILE = '/app/whatsapp-bridge/qrcode.png'

@app.route('/')
def root():
    return jsonify({"status": "running", "bot": BOT_NAME})

@app.route('/health')
def health():
    return jsonify({"status": "ok", "bot": BOT_NAME})

@app.route('/qr')
def qr_code():
    if os.path.exists(QR_FILE):
        return send_file(QR_FILE, mimetype='image/png')
    return jsonify({"error": "QR Code ainda nao gerado"}), 404

@app.route('/debug')
def debug():
    all_files = []
    for root_dir, dirs, files in os.walk('/app'):
        dirs[:] = [d for d in dirs if d != 'node_modules']
        for f in files:
            if not f.endswith('.pyc'):
                full = os.path.join(root_dir, f)
                size = os.path.getsize(full)
                all_files.append({"path": full, "size": size})

    log_content = {}
    for lf in glob.glob('/app/*.log'):
        try:
            with open(lf) as f:
                log_content[os.path.basename(lf)] = f.read()[-3000:]
        except:
            pass

    return jsonify({
        "port": os.environ.get('PORT', 'not set'),
        "qr_exists": os.path.exists(QR_FILE),
        "auth_exists": os.path.exists('/app/whatsapp-bridge/auth_state'),
        "files": all_files,
        "logs": log_content
    })

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
    print(f"API do {BOT_NAME} em http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
