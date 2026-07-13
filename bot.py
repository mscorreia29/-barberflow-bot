# WhatsApp Bot BarberFlow - Logica Principal (v5)
from datetime import datetime
from config import BOT_NAME, IGNORE_GROUPS
from ai_handler import get_ai_response, should_transfer_to_human
from knowledge_base import QUICK_RESPONSES, SAUDACOES
import logging
import re

logger = logging.getLogger(__name__)

KEYWORD_RESPONSES = {
    # Saudacao
    "oi": "/ola", "ola": "/ola", "bom dia": "/ola", "boa tarde": "/ola",
    "boa noite": "/ola", "e ai": "/ola", "fala": "/ola", "hello": "/ola",
    "hi": "/ola", "hey": "/ola", "eae": "/ola",
    
    # Agradecimento
    "obrigado": "/obrigado", "obrigada": "/obrigado", "valeu": "/obrigado",
    "vlw": "/obrigado", "thanks": "/obrigado", "brigado": "/obrigado",
    
    # Teste gratis
    "quero testar": "/teste", "quero experimentar": "/teste",
    "teste gratis": "/teste", "teste gratuito": "/teste",
    "testar gratis": "/teste", "7 dias": "/teste", "sete dias": "/teste",
    
    # Cadastro
    "criar conta": "/cadastrar", "criar minha conta": "/cadastrar",
    "quero me cadastrar": "/cadastrar", "como cadastro": "/cadastrar",
    "registrar": "/cadastrar",
    
    # Login
    "esqueci a senha": "/login", "acessar minha conta": "/login",
    "entrar na conta": "/login", "minha conta": "/login",
    "recuperar senha": "/login", "trocar senha": "/login",
    
    # App
    "tem app": "/app", "tem aplicativo": "/app",
    "funciona no celular": "/compatibilidade", "funciona no pc": "/compatibilidade",
    "funciona no computador": "/compatibilidade", "funciona no iphone": "/compatibilidade",
    "funciona no android": "/compatibilidade",
    "link do app": "/app", "link do sistema": "/app",
    "preciso instalar": "/app", "preciso baixar": "/app",
    
    # Site
    "qual o site": "/site", "site oficial": "/site",
    "link do site": "/site", "site do barberflow": "/site",
    
    # Manual
    "tem manual": "/manual", "tutorial": "/manual",
    
    # Como funciona
    "como funciona": "/como", "me explica como funciona": "/como",
    "como funciona o barberflow": "/como", "como que funciona": "/como",
    "como funciona o sistema": "/como", "como funciona o app": "/como",
    
    # Planos
    "quanto custa": "/planos", "quanto e o plano": "/planos",
    "valor do plano": "/planos", "mensalidade": "/planos",
    "preco do barberflow": "/planos", "planos e precos": "/planos",
    "quais planos": "/planos", "tem plano": "/planos",
    "plano basico": "/planos", "plano pro": "/planos",
    "custa quanto": "/planos", "quanto e": "/planos",
    
    # Recursos
    "o que o barberflow faz": "/recurso", "o que tem no barberflow": "/recurso",
    "funcionalidades do barberflow": "/recurso", "quais recursos": "/recurso",
    "tem estoque": "/recurso", "comissao": "/recurso", "comissoes": "/recurso",
    "mercado pago": "/recurso", "dashboard": "/recurso",
    "relatorio": "/recurso", "relatorios": "/recurso",
    "avaliacao": "/recurso", "avaliacoes": "/recurso",
    
    # WhatsApp
    "integracao whatsapp": "/whatsapp", "notificacao whatsapp": "/whatsapp",
    "lembrete whatsapp": "/whatsapp",
    
    # Notificacoes
    "notificacao": "/notificacoes", "notificação": "/notificacoes",
    "lembrete automatico": "/notificacoes", "lembretes": "/notificacoes",
    
    # Assinaturas
    "assinatura recorrente": "/assinaturas", "cobranca recorrente": "/assinaturas",
    
    # Compartilhar
    "compartilhar link": "/compartilhar", "link pros clientes": "/compartilhar",
    "como mando pro cliente": "/compartilhar",
    
    # Suporte
    "falar com atendente": "/humano", "falar com suporte": "/humano",
    "horario de atendimento": "/horarios", "contato do suporte": "/horarios",
    "suporte": "/humano",
    
    # Cancelar
    "quero cancelar": "/cancelar", "como cancelo": "/cancelar",
    "cancelar plano": "/cancelar", "cancelar assinatura": "/cancelar",
    
    # Sugestoes
    "sugestao": "/sugestao", "sugiro": "/sugestao", "melhoria": "/sugestao",
    "melhorar": "/sugestao", "seria legal": "/sugestao", "podia ter": "/sugestao",
    "ideia": "/sugestao", "feedback": "/feedback", "critica": "/feedback",
    
    # Barbeiro
    "como cadastro barbeiro": "/barbeiro", "como adicionar barbeiro": "/barbeiro",
    "cadastrar barbeiro": "/barbeiro", "adicionar barbeiro": "/barbeiro",
    "acesso barbeiro": "/barbeiro", "enviar acesso barbeiro": "/barbeiro",
    "vincular barbeiro": "/barbeiro",
    
    # === COBRANCAS ===
    "pagamento": "/pagamento", "status pagamento": "/pagamento",
    "meu pagamento": "/pagamento", "paguei": "/pagamento",
    "pix": "/pix_pagamento", "chave pix": "/pix_pagamento",
    "boleto": "/pix_pagamento",
    
    # === AGENDAMENTO ===
    "agendar": "/agendar", "marcar horario": "/agendar",
    "agendamento": "/agendar", "horario disponivel": "/agendar",
    "ver agenda": "/ver_agenda", "minha agenda": "/ver_agenda",
    "consultar agenda": "/ver_agenda",
    
    # === MARKETING ===
    "promocao": "/promocao", "divulgar": "/promocao",
    "campanha": "/promocao", "desconto": "/promocao",
}

PROBLEM_KEYWORDS = [
    "problema", "erro", "bug", "defeito", "nao funciona", "não funciona",
    "ta dando erro", "esta dando erro", "deu erro", "apareceu erro",
    "nao consigo", "não consigo", "nao abre", "não abre", "travou",
    "lento", "carregando", "fora do ar", "caiu", "instavel",
    "nao carrega", "não carrega", "carregando infinito",
    "site publico", "site caiu", "app caiu", "sistema caiu",
    "nao ta funcionando", "parou de funcionar",
    "nao consigo agendar", "agenda nao atualiza",
    "cliente nao recebe", "notificacao nao chega"
]


class WhatsAppBot:
    def __init__(self):
        self.conversations = {}
        self.transfer_users = set()
    
    def _find_quick_response(self, message: str) -> str | None:
        msg_lower = message.lower().strip()
        words_count = len(msg_lower.split())
        
        for prob in PROBLEM_KEYWORDS:
            if prob in msg_lower:
                return None
        
        if msg_lower in QUICK_RESPONSES:
            return QUICK_RESPONSES[msg_lower]
        
        if words_count <= 2 and any(s in msg_lower for s in SAUDACOES):
            return QUICK_RESPONSES.get("/ola")
        
        sorted_keywords = sorted(KEYWORD_RESPONSES.items(), key=lambda x: len(x[0]), reverse=True)
        for keyword, response_key in sorted_keywords:
            if keyword in msg_lower:
                if words_count > 3 and len(keyword.split()) <= 1:
                    continue
                if words_count > 4 and len(keyword.split()) <= 2:
                    continue
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
        
        quick_response = self._find_quick_response(message)
        if quick_response:
            self.conversations[phone].append({"role": "user", "content": message})
            self.conversations[phone].append({"role": "assistant", "content": quick_response})
            return quick_response
        
        if should_transfer_to_human(message):
            self.transfer_users.add(phone)
            return QUICK_RESPONSES["/humano"]
        
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
