# WhatsApp Bot BarberFlow - Logica Principal (v4)
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
    "eae": "/ola",
    
    # Agradecimento
    "obrigado": "/obrigado",
    "obrigada": "/obrigado",
    "valeu": "/obrigado",
    "vlw": "/obrigado",
    "thanks": "/obrigado",
    "brigado": "/obrigado",
    
    # Teste gratis
    "quero testar": "/teste",
    "quero experimentar": "/teste",
    "teste gratis": "/teste",
    "teste gratuito": "/teste",
    "testar gratis": "/teste",
    "7 dias": "/teste",
    "sete dias": "/teste",
    "quero o teste": "/teste",
    
    # Cadastro
    "criar conta": "/cadastrar",
    "criar minha conta": "/cadastrar",
    "quero me cadastrar": "/cadastrar",
    "como cadastro": "/cadastrar",
    "como criar conta": "/cadastrar",
    "registrar": "/cadastrar",
    
    # Login
    "esqueci a senha": "/login",
    "acessar minha conta": "/login",
    "entrar na conta": "/login",
    "minha conta": "/login",
    "recuperar senha": "/login",
    "trocar senha": "/login",
    
    # App/Sistema - frases completas
    "como entro no app": "/app",
    "onde entra no sistema": "/app",
    "onde acesso o sistema": "/app",
    "como acesso o barberflow": "/app",
    "onde baixo o app": "/app",
    "link do app": "/app",
    "link do sistema": "/app",
    "tem app": "/app",
    "tem aplicativo": "/app",
    "funciona no celular": "/compatibilidade",
    "funciona no pc": "/compatibilidade",
    "funciona no computador": "/compatibilidade",
    "funciona no iphone": "/compatibilidade",
    "funciona no android": "/compatibilidade",
    "funciona em qualquer": "/compatibilidade",
    "preciso instalar": "/app",
    "preciso baixar": "/app",
    
    # Site
    "qual o site": "/site",
    "site oficial": "/site",
    "endereco do site": "/site",
    "link do site": "/site",
    "site do barberflow": "/site",
    
    # Manual
    "tem manual": "/manual",
    "manual do barberflow": "/manual",
    "como usar o barberflow": "/como",
    "tutorial": "/manual",
    
    # Como funciona
    "como funciona": "/como",
    "me explica como funciona": "/como",
    "como funciona o barberflow": "/como",
    "como que funciona": "/como",
    "como funciona o sistema": "/como",
    "como funciona o app": "/como",
    
    # Planos
    "quanto custa": "/planos",
    "quanto e o plano": "/planos",
    "quanto vale": "/planos",
    "valor do plano": "/planos",
    "mensalidade": "/planos",
    "preco do barberflow": "/planos",
    "planos e precos": "/planos",
    "quais planos": "/planos",
    "tem plano": "/planos",
    "plano basico": "/planos",
    "plano pro": "/planos",
    "quanto e": "/planos",
    "preco": "/planos",
    "custa quanto": "/planos",
    
    # Recursos
    "o que o barberflow faz": "/recurso",
    "o que tem no barberflow": "/recurso",
    "funcionalidades do barberflow": "/recurso",
    "quais recursos": "/recurso",
    "o que e o barberflow": "/recurso",
    "tem estoque": "/recurso",
    "controle de estoque": "/recurso",
    "avaliacao": "/recurso",
    "avaliacoes": "/recurso",
    "relatorio": "/recurso",
    "relatorios": "/recurso",
    "dashboard": "/recurso",
    "comissao": "/recurso",
    "comissoes": "/recurso",
    "mercado pago": "/recurso",
    
    # WhatsApp
    "integracao whatsapp": "/whatsapp",
    "integracao com whatsapp": "/whatsapp",
    "envia mensagem automatica": "/whatsapp",
    "mensagem automatica whatsapp": "/whatsapp",
    "notificacao whatsapp": "/whatsapp",
    "lembrete whatsapp": "/whatsapp",
    
    # Notificacoes
    "notificacao": "/notificacoes",
    "notificação": "/notificacoes",
    "lembrete automatico": "/notificacoes",
    "lembretes": "/notificacoes",
    
    # Assinaturas
    "assinatura recorrente": "/assinaturas",
    "cobranca recorrente": "/assinaturas",
    
    # Compartilhar link
    "compartilhar link": "/compartilhar",
    "link pros clientes": "/compartilhar",
    "como mando pro cliente": "/compartilhar",
    "como compartilho": "/compartilhar",
    
    # Suporte
    "falar com atendente": "/humano",
    "falar com suporte": "/humano",
    "horario de atendimento": "/horarios",
    "telefone do suporte": "/horarios",
    "contato do suporte": "/horarios",
    "suporte": "/humano",
    
    # Cancelar
    "quero cancelar": "/cancelar",
    "como cancelo": "/cancelar",
    "cancelar plano": "/cancelar",
    "cancelar assinatura": "/cancelar",
    
    # Sugestoes
    "sugestao": "/sugestao",
    "sugiro": "/sugestao",
    "melhoria": "/sugestao",
    "melhorar": "/sugestao",
    "seria legal": "/sugestao",
    "podia ter": "/sugestao",
    "ideia": "/sugestao",
    "feedback": "/feedback",
    "critica": "/feedback",
    
    # Barbeiro
    "como cadastro barbeiro": "/barbeiro",
    "como adicionar barbeiro": "/barbeiro",
    "cadastrar barbeiro": "/barbeiro",
    "adicionar barbeiro": "/barbeiro",
    "acesso barbeiro": "/barbeiro",
    "enviar acesso barbeiro": "/barbeiro",
    "barbeiro nao recebe": "/barbeiro",
    "como mando acesso barbeiro": "/barbeiro",
    "vincular barbeiro": "/barbeiro",
}

# Palavras que indicam PROBLEMA - ir direto pra IA
PROBLEM_KEYWORDS = [
    "problema", "erro", "bug", "defeito", "nao funciona", "não funciona",
    "ta dando erro", "esta dando erro", "deu erro", "apareceu erro",
    "nao consigo", "não consigo", "nao abre", "não abre", "travou",
    "lento", "carregando", "fora do ar", "caiu", "instavel",
    "nao carrega", "não carrega", "carregando infinito",
    "site publico", "site caiu", "app caiu", "sistema caiu",
    "nao ta funcionando", "não tá funcionando", "parou de funcionar",
    "navegador", "cache", "cookies", "internet",
    "compativel", "compatível", "suporta", "funciona no",
    "android", "iphone", "celular", "computador",
    "nao consigo agendar", "não consigo agendar",
    "agenda nao atualiza", "agenda nao aparece",
    "cliente nao recebe", "cliente não recebe",
    "notificacao nao chega", "mensagem nao envia"
]


class WhatsAppBot:
    def __init__(self):
        self.conversations = {}
        self.transfer_users = set()
        self.first_message = set()
    
    def _find_quick_response(self, message: str) -> str | None:
        msg_lower = message.lower().strip()
        words_count = len(msg_lower.split())
        
        # Se tem palavras de PROBLEMA, ir pra IA
        for prob in PROBLEM_KEYWORDS:
            if prob in msg_lower:
                return None
        
        # Respostas rapidas exatas
        if msg_lower in QUICK_RESPONSES:
            return QUICK_RESPONSES[msg_lower]
        
        # Saudacao simples
        if words_count <= 2 and any(s in msg_lower for s in SAUDACOES):
            return QUICK_RESPONSES.get("/ola")
        
        # Buscar frases-chave (mais longas primeiro)
        sorted_keywords = sorted(KEYWORD_RESPONSES.items(), key=lambda x: len(x[0]), reverse=True)
        for keyword, response_key in sorted_keywords:
            if keyword in msg_lower:
                # Pra keywords curtas (1-2 palavras), so match se msg for curta
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
        
        # 1. Resposta rapida
        quick_response = self._find_quick_response(message)
        if quick_response:
            self.conversations[phone].append({"role": "user", "content": message})
            self.conversations[phone].append({"role": "assistant", "content": quick_response})
            return quick_response
        
        # 2. Transferencia pra humano
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
