# WhatsApp Bot BarberFlow - Logica Principal (v2)
from datetime import datetime
from config import BOT_NAME, IGNORE_GROUPS
from ai_handler import get_ai_response, should_transfer_to_human
from knowledge_base import QUICK_RESPONSES, SAUDACOES
import logging

logger = logging.getLogger(__name__)

KEYWORD_RESPONSES = {
    # Saudacao
    "oi": "/ola",
    "ola": "/ola",
    "bom dia": "/ola",
    "boa tarde": "/ola",
    "boa noite": "/ola",
    "e ai": "/ola",
    "fala": "/ola",
    "hello": "/ola",
    "hi": "/ola",
    "hey": "/ola",
    
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
    "quero testar": "/teste",
    "quero experimentar": "/teste",
    
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
    "quero me cadastrar": "/cadastrar",
    "como cadastro": "/cadastrar",
    
    # Login
    "login": "/login",
    "entrar": "/login",
    "logar": "/login",
    "acessar minha conta": "/login",
    "minha conta": "/login",
    "esqueci a senha": "/login",
    "entrar na conta": "/login",
    
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
    "como entro": "/app",
    "onde baixo": "/app",
    
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
    "como funciona": "/como",
    "me explica": "/como",
    "como que e": "/como",
    "como funciona o barberflow": "/como",
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
    "quanto e": "/planos",
    "quanto vale": "/planos",
    "mensalidade": "/planos",
    
    # Recursos
    "recurso": "/recurso",
    "recursos": "/recurso",
    "funcionalidade": "/recurso",
    "funcionalidades": "/recurso",
    "o que faz": "/recurso",
    "o que tem": "/recurso",
    "o que e": "/recurso",
    "tem o que": "/recurso",
    
    # WhatsApp
    "whatsapp": "/whatsapp",
    "zapi": "/whatsapp",
    "integracao whatsapp": "/whatsapp",
    "integração whatsapp": "/whatsapp",
    "mensagem automatica": "/whatsapp",
    "envia mensagem": "/whatsapp",
    
    # Notificacoes
    "notificacao": "/notificacoes",
    "notificação": "/notificacoes",
    "notificacoes": "/notificacoes",
    "notificações": "/notificacoes",
    "push": "/notificacoes",
    "lembrete": "/notificacoes",
    "lembretes": "/notificacoes",
    "aviso": "/notificacoes",
    
    # Assinaturas
    "assinatura": "/assinaturas",
    "assinaturas": "/assinaturas",
    "recorrente": "/assinaturas",
    "mensal": "/assinaturas",
    "recorrencia": "/assinaturas",
    "cobranca": "/assinaturas",
    
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
    "telefone": "/horarios",
    "whatsapp suporte": "/humano",
    
    # Cancelar
    "cancelar": "/cancelar",
    "cancelamento": "/cancelar",
    "desistir": "/cancelar",
    "quero cancelar": "/cancelar",
    
    # Barbeiro/Agendamento
    "barbeiro": "/recurso",
    "agendamento": "/recurso",
    "agendar": "/recurso",
    "comissao": "/recurso",
    "comissao barbeiro": "/recurso",
    
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
        msg_lower = message.lower().strip()
        
        # Respostas rapidas exatas
        if msg_lower in QUICK_RESPONSES:
            return QUICK_RESPONSES[msg_lower]
        
        # Saudacao simples (so 1-2 palavras)
        words = msg_lower.split()
        if len(words) <= 2 and any(s in msg_lower for s in SAUDACOES):
            return QUICK_RESPONSES.get("/ola")
        
        # Buscar palavras-chave (mais longas primeiro)
        sorted_keywords = sorted(KEYWORD_RESPONSES.items(), key=lambda x: len(x[0]), reverse=True)
        for keyword, response_key in sorted_keywords:
            if keyword in msg_lower:
                if response_key.startswith("/"):
                    return QUICK_RESPONSES.get(response_key)
                return response_key
        
        return None
    
    def handle_message(self, phone: str, message: str, is_group: bool = False) -> str:
        if is_group and IGNORE_GROUPS:
            return None
        
        phone = phone.replace("@s.whatsapp.net", "").replace("@g.us", "")
        
        if phone in self.transfer_users:
            return "Atendente ira atende-lo em breve. Aguarde!"
        
        if phone not in self.conversations:
            self.conversations[phone] = []
        
        message = message.strip()
        
        # 1. Resposta rapida (links)
        quick_response = self._find_quick_response(message)
        if quick_response:
            self.conversations[phone].append({"role": "user", "content": message})
            self.conversations[phone].append({"role": "assistant", "content": quick_response})
            return quick_response
        
        # 2. Transferencia para humano
        if should_transfer_to_human(message):
            self.transfer_users.add(phone)
            return QUICK_RESPONSES["/humano"]
        
        # 3. IA
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
