# Teste rapido do bot
import sys
sys.path.insert(0, 'C:\\Users\\Matheus\\whatsapp-bot-barbearia')

from bot import bot

print("=== TESTE DO BOT ===")
print()

# Teste 1: Comando /ajuda
print("[Teste 1] /ajuda")
resp = bot.handle_message("5511999999999", "/ajuda")
print(f"Resposta: {resp}")
print()

# Teste 2: Comando /planos
print("[Teste 2] /planos")
resp = bot.handle_message("5511999999999", "/planos")
print(f"Resposta: {resp}")
print()

# Teste 3: Pergunta sobre sistema
print("[Teste 3] Como agendar?")
resp = bot.handle_message("5511888888888", "Como faço para agendar um cliente?")
print(f"Resposta: {resp}")
print()

# Teste 4: Falar com humano
print("[Teste 4] /humano")
resp = bot.handle_message("5511777777777", "/humano")
print(f"Resposta: {resp}")
print()

# Estatisticas
print("=== ESTATISTICAS ===")
stats = bot.get_stats()
print(f"Total de conversas: {stats['total_conversations']}")
print(f"Transferidos: {stats['transferred_users']}")
print()

print("=== TESTE CONCLUIDO ===")
