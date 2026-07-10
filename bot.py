# WhatsApp Bot BarberFlow - Logica Principal
from datetime import datetime
from config import BOT_NAME, IGNORE_GROUPS
from ai_handler import get_ai_response, should_transfer_to_human
from knowledge_base import QUICK_RESPONSES
import logging

logger = logging.getLogger(__name__)

# Palavras-chave que DEVEM retornar respostas rapidas (links)
KEYWORD_RESPONSES = {
    # Teste gratis
    "teste": "/teste",
    "testar": "/teste",
    "gratis": "/teste",
    "gratuito": "/teste",
    "trial": "/teste",
    "experimentar": "/teste",
    "testar gratis": "/teste",
    "teste gratis": "/teste",
    "7 dias": "/teste",
    "sete dias": "/teste",
    
    # Cadastro
    "cadastrar": "/cadastrar",
    "cadastro": "/cadastrar",
    "criar conta": "/cadastrar",
    "criar minha conta": "/cadastrar",
    "registrar": "/cadastrar",
    "inscrever": "/cadastrar",
    "comecar": "/cadastrar",
    "começar": "/cadastrar",
    "quero comecar": "/cadastrar",
    "quero começar": "/cadastrar",
    
    # Login
    "login": "/login",
    "entrar": "/login",
    "logar": "/login",
    "acessar minha conta": "/login",
    "minha conta": "/login",
    "esqueci a senha": "/login",
    
    # App/Sistema
    "app": "/app",
    "aplicativo": "/app",
    "sistema": "/app",
    "acessar": "/app",
    "abrir": "/app",
    "entrar no sistema": "/app",
    "onde entra": "/app",
    "onde acesso": "/app",
    "link": "/app",
    "url": "/app",
    
    # Site
    "site": "/site",
    "website": "/site",
    "pagina": "/site",
    "pagina oficial": "/site",
    
    # Manual
    "manual": "/manual",
    "tutorial": "/manual",
    "como usar": "/como",
    "como funciona": "/como",
    "como comeca": "/como",
    "como começa": "/como",
    "instrucoes": "/manual",
    "instruções": "/manual",
    "ajuda completa": "/manual",
    
    # Planos
    "preco": "/planos",
    "preço": "/planos",
    "quanto custa": "/planos",
    "valor": "/planos",
    "planos": "/planos",
    "plano": "/planos",
    "basico": "/planos",
    "básico": "/planos",
    "pro": "/planos",
    "profissional": "/planos",
    
    # Recursos
    "recurso": "/recurso",
    "recursos": "/recurso",
    "funcionalidade": "/recurso",
    "funcionalidades": "/recurso",
    "o que faz": "/recurso",
    "o que tem": "/recurso",
    
    # WhatsApp
    "whatsapp": "/whatsapp",
    "zapi": "/whatsapp",
    "integracao whatsapp": "/whatsapp",
    "integração whatsapp": "/whatsapp",
    "mensagem automatica": "/whatsapp",
    
    # Notificacoes
    "notificacao": "/notificacoes",
    "notificação": "/notificacoes",
    "notificacoes": "/notificacoes",
    "notificações": "/notificacoes",
    "push": "/notificacoes",
    "lembrete": "/notificacoes",
    "lembretes": "/notificacoes",
    
    # Assinaturas
    "assinatura": "/assinaturas",
    "assinaturas": "/assinaturas",
    "recorrente": "/assinaturas",
    "mensal": "/assinaturas",
    "recorrencia": "/assinaturas",
    
    # Suporte
    "suporte": "/humano",
    "atendente": "/humano",
    "humano": "/humano",
    "pessoa": "/humano",
    "falar com": "/humano",
    "contato": "/horarios",
    "horario": "/horarios",
    "horário": "/horarios",
    "funcionamento": "/horarios",
    
    # Cancelar
    "cancelar": "Para cancelar, acesse Configuracoes > Plano no painel. Sem multa.",
    "cancelamento": "Para cancelar, acesse Configuracoes > Plano no painel. Sem multa.",
    "desistir": "Para cancelar, acesse Configuracoes > Plano no painel. Sem multa.",
    
    # Preco especifico
    "49": "/planos",
    "89": "/planos",
    "49,90": "/planos",
    "89,90": "/planos",
}

class WhatsAppBot:
    def __init__(self):
        self.conversations = {}
        self.transfer_users = set()
    
    def _find_quick_response(self, message: str) -> str | None:
        """Busca resposta rapida baseada em palavras-chave"""
        msg_lower = message.lower().strip()
        
        # Verificar respostas rapidas exatas primeiro
        if msg_lower in QUICK_RESPONSES:
            return QUICK_RESPONSES[msg_lower]
        
        # Buscar palavras-chave
        for keyword, response_key in KEYWORD_RESPONSES.items():
            if keyword in msg_lower:
                if response_key.startswith("/"):
                    return QUICK_RESPONSES.get(response_key)
                return response_key
        
        return None
    
    def handle_message(self, phone: str, message: str, is_group: bool = False) -> str:
        """Processa mensagem e retorna resposta"""
        
        if is_group and IGNORE_GROUPS:
            return None
        
        phone = phone.replace("@s.whatsapp.net", "").replace("@g.us", "")
        
        if phone in self.transfer_users:
            return "Atendente ira atende-lo em breve. Aguarde."
        
        if phone not in self.conversations:
            self.conversations[phone] = []
        
        message = message.strip()
        
        # 1. Tentar resposta rapida (links)
        quick_response = self._find_quick_response(message)
        if quick_response:
            self.conversations[phone].append({"role": "user", "content": message})
            self.conversations[phone].append({"role": "assistant", "content": quick_response})
            return quick_response
        
        # 2. Verificar transferencia para humano
        if should_transfer_to_human(message):
            self.transfer_users.add(phone)
            return QUICK_RESPONSES["/humano"]
        
        # 3. Usar IA (para perguntas complexas)
        response = get_ai_response(message, self.conversations[phone])
        
        self.conversations[phone].append({"role": "user", "content": message})
        self.conversations[phone].append({"role": "assistant", "content": response})
        self.conversations[phone] = self.conversations[phone][-8:]
        
        return response
    
    def get_stats(self) -> dict:
        return {
            "total_conversations": len(self.conversations),
            "transferred_users": len(self.transfer_users),
            "active_conversations": sum(1 for h in self.conversations.values() if h)
        }

bot = WhatsAppBot()
