# Teste final do sistema completo
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== TESTE DO SISTEMA BARBERFLOW BOT ===\n")

# 1. Testar bot
print("[1] Testando bot...")
from bot import bot
resp = bot.handle_message("5511999999999", "/ajuda")
print(f"    Bot: {'OK' if resp else 'FALHOU'}")

# 2. Testar API
print("[2] Testando API...")
from api_server import app
print(f"    API: OK (Flask)")

# 3. Testar Groq
print("[3] Testando Groq IA...")
from ai_handler import get_ai_response
resp = get_ai_response("Ola")
print(f"    Groq: {'OK' if resp else 'FALHOU'}")

# 4. Verificar WhatsApp Bridge
print("[4] Verificando WhatsApp Bridge...")
bridge_path = os.path.join(os.path.dirname(__file__), 'whatsapp-bridge', 'index.js')
if os.path.exists(bridge_path):
    print("    Bridge: OK (arquivo existe)")
else:
    print("    Bridge: FALHOU (arquivo nao encontrado)")

print("\n=== TESTE CONCLUIDO ===")
print("\nPara iniciar o bot completo:")
print("  python main.py")
print("  Escolha opcao 2")
print("  Escaneie o QR Code")
