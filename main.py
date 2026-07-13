# WhatsApp Bot AutoAssist - Interface Principal
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot import bot
from config import BOT_NAME, SUPPORT_HOURS

def print_banner():
    """Exibe banner do bot"""
    print("=" * 50)
    print("  BARBERFLOW WHATSAPP BOT")
    print("=" * 50)
    print()
    print("  Opcoes:")
    print("    1 - Testar bot (digite mensagens)")
    print("    2 - Iniciar API + WhatsApp Bridge")
    print("    3 - Apenas API Server")
    print("    0 - Sair")
    print()
    print("=" * 50)
    print()

def test_bot():
    """Testa o bot com mensagens simuladas"""
    print()
    print("Modo teste - Digite mensagens para testar")
    print("Use: numero:mensagem (ex: 5511999999999:ola)")
    print("Para sair digite: sair")
    print()
    
    while True:
        try:
            user_input = input("Voce: ").strip()
            
            if user_input.lower() == 'sair':
                print("Saindo do teste...")
                break
            
            if user_input.lower() == 'stats':
                stats = bot.get_stats()
                print()
                print("Estatisticas:")
                print(f"  Total conversas: {stats['total_conversations']}")
                print(f"  Transferidos: {stats['transferred_users']}")
                print()
                continue
            
            if ':' in user_input:
                phone, message = user_input.split(':', 1)
            else:
                phone = "5511999999999"
                message = user_input
            
            response = bot.handle_message(phone, message)
            
            if response:
                print()
                print(f"Bot: {response}")
                print()
            else:
                print("(ignorado)")
                
        except KeyboardInterrupt:
            print()
            print("Saindo...")
            break
        except Exception as e:
            print(f"Erro: {e}")

def start_api_server():
    """Inicia o servidor API"""
    from api_server import app
    print()
    print("API Server rodando em http://127.0.0.1:5000")
    print("Pressione Ctrl+C para parar")
    print()
    app.run(host='127.0.0.1', port=5000, debug=False)

def start_api_and_bridge():
    """Inicia API e WhatsApp Bridge"""
    import threading
    import time
    import subprocess
    
    print()
    print("Iniciando API Server...")
    
    # Iniciar API em thread
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()
    
    time.sleep(2)
    print("API iniciada!")
    print()
    print("Iniciando WhatsApp Bridge...")
    print("Escaneie o QR Code com seu WhatsApp")
    print()
    
    # Iniciar bridge
    bridge_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'whatsapp-bridge')
    
    try:
        subprocess.run(['node', 'index.js'], cwd=bridge_dir)
    except FileNotFoundError:
        print("ERRO: Node.js nao encontrado!")
        print("Instale em: https://nodejs.org")
    except KeyboardInterrupt:
        print()
        print("Bridge parado.")

def main():
    """Funcao principal"""
    print_banner()
    
    while True:
        try:
            choice = input("Escolha (0-3): ").strip()
            
            if choice == '1':
                test_bot()
                print_banner()
            elif choice == '2':
                start_api_and_bridge()
            elif choice == '3':
                start_api_server()
            elif choice == '0':
                print("Saindo...")
                break
            else:
                print("Opcao invalida! Use 0, 1, 2 ou 3")
                print()
                
        except KeyboardInterrupt:
            print()
            print("Saindo...")
            break
        except Exception as e:
            print(f"Erro: {e}")

if __name__ == "__main__":
    main()
