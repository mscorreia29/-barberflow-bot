# WhatsApp Bot BarberFlow - Logica Principal (v3)
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
    "quero testar": "/teste",
    "quero experimentar": "/teste",
    "teste gratis": "/teste",
    "teste gratuito": "/teste",
    "testar gratis": "/teste",
    "7 dias": "/teste",
    "sete dias": "/teste",
    
    # Cadastro
    "criar conta": "/cadastrar",
    "criar minha conta": "/cadastrar",
    "quero me cadastrar": "/cadastrar",
    "como cadastro": "/cadastrar",
    "como criar conta": "/cadastrar",
    
    # Login
    "esqueci a senha": "/login",
    "acessar minha conta": "/login",
    "entrar na conta": "/login",
    "minha conta": "/login",
    "recuperar senha": "/login",
    
    # App/Sistema - so frases completas
    "como entro no app": "/app",
    "onde entra no sistema": "/app",
    "onde acesso o sistema": "/app",
    "como acesso o barberflow": "/app",
    "onde baixo o app": "/app",
    "link do app": "/app",
    "link do sistema": "/app",
    
    # Site - so frases completas
    "qual o site": "/site",
    "site oficial": "/site",
    "endereco do site": "/site",
    "link do site": "/site",
    
    # Manual - so frases completas
    "tem manual": "/manual",
    "manual do barberflow": "/manual",
    "como usar o barberflow": "/como",
    
    # Como funciona - frases
    "como funciona": "/como",
    "me explica como funciona": "/como",
    "como funciona o barberflow": "/como",
    "como que funciona": "/como",
    "como funciona o sistema": "/como",
    
    # Planos - frases completas
    "quanto custa": "/planos",
    "quanto e o plano": "/planos",
    "quanto vale": "/planos",
    "valor do plano": "/planos",
    "mensalidade": "/planos",
    "preco do barberflow": "/planos",
    "planos e precos": "/planos",
    "quais planos": "/planos",
    "tem plano": "/planos",
    
    # Recursos - frases
    "o que o barberflow faz": "/recurso",
    "o que tem no barberflow": "/recurso",
    "funcionalidades do barberflow": "/recurso",
    "quais recursos": "/recurso",
    "o que e o barberflow": "/recurso",
    
    # WhatsApp - frases
    "integracao whatsapp": "/whatsapp",
    "integracao com whatsapp": "/whatsapp",
    "envia mensagem automatica": "/whatsapp",
    "mensagem automatica whatsapp": "/whatsapp",
    
    # Notificacoes
    "notificacao": "/notificacoes",
    "notificação": "/notificacoes",
    "lembrete automatico": "/notificacoes",
    "lembretes": "/notificacoes",
    
    # Assinaturas
    "assinatura recorrente": "/assinaturas",
    "cobranca recorrente": "/assinaturas",
    
    # Suporte - frases
    "falar com atendente": "/humano",
    "falar com suporte": "/humano",
    "suporte humano": "/horarios",
    "horario de atendimento": "/horarios",
    "telefone do suporte": "/horarios",
    "contato do suporte": "/horarios",
    
    # Cancelar
    "quero cancelar": "/cancelar",
    "como cancelo": "/cancelar",
    "cancelar plano": "/cancelar",
    "cancelar assinatura": "/cancelar",
}

# Palavras que indicam PROBLEMA - devem ir direto pra IA
PROBLEM_KEYWORDS = [
    "problema", "erro", "bug", "defeito", "nao funciona", "não funciona",
    "ta dando erro", "esta dando erro", "deu erro", "apareceu erro",
    "nao consigo", "não consigo", "nao abre", "não abre", "travou",
    "lento", "carregando", "fora do ar", "caiu", "instavel",
    "problem", "trouble", "issue", "not working",
    "nao carrega", "não carrega", "carregando infinito",
    "site publico", "site caiu", "app caiu", "sistema caiu",
    "nao ta funcionando", "não tá funcionando", "parou de funcionar",
    "navegador", "cache", "cookies", "internet",
    "compativel", "compatível", "suporta", "funciona no",
    "android", "iphone", "celular", "computador"
]

# Palavras que indicam duvida sobre funcionamento
HOW_IT_WORKS_KEYWORDS = [
    "como funciona", "como que e", "como e", "me explica",
    "o que faz", "o que e", "pra que serve", "qual a funcao",
    "como usa", "como usar", "como começo", "como comecar",
    "como faço", "como faco", "como configura",
    "quero saber", "me conta mais", "explica"
]


class WhatsAppBot:
    def __init__(self):
        self.conversations = {}
        self.transfer_users = set()
    
    def _find_quick_response(self, message: str) -> str | None:
        msg_lower = message.lower().strip()
        words_count = len(msg_lower.split())
        
        # Se tem palavras de PROBLEMA, NUNCA retornar resposta rapida
        # Sempre mandar pra IA que tem mais contexto
        for prob in PROBLEM_KEYWORDS:
            if prob in msg_lower:
                return None
        
        # Respostas rapidas exatas
        if msg_lower in QUICK_RESPONSES:
            return QUICK_RESPONSES[msg_lower]
        
        # Saudacao simples
        if words_count <= 2 and any(s in msg_lower for s in SAUDACOES):
            return QUICK_RESPONSES.get("/ola")
        
        # Buscar frases-chave (mais longas primeiro pra nao pegar substrings)
        sorted_keywords = sorted(KEYWORD_RESPONSES.items(), key=lambda x: len(x[0]), reverse=True)
        for keyword, response_key in sorted_keywords:
            if keyword in msg_lower:
                # Pra keywords curtas (1 palavra), so match se a mensagem for curta
                if words_count > 3 and len(keyword.split()) == 1:
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
