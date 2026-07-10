# Base de Conhecimento - BarberFlow (v2)
# Respostas curtas e efetivas

KNOWLEDGE_BASE = {
    "sistema": {
        "nome": "BarberFlow",
        "url_site": "https://barber-flow.store",
        "url_app": "https://barber-flow.store/barberflow",
        "url_cadastro": "https://barber-flow.store/auth?mode=signup",
        "url_login": "https://barber-flow.store/auth",
        "url_manual": "https://barber-flow.store/manual",
        "funcionalidades": [
            "Agendamento online 24h",
            "Painel administrativo",
            "Dashboard com indicadores",
            "Gerenciamento de agenda",
            "Cadastro de clientes e servicos",
            "Comissoes automaticas",
            "Relatorios de faturamento",
            "Notificacoes push",
            "Integracao WhatsApp",
            "Assinaturas recorrentes",
            "Controle de estoque",
            "Avaliacoes de clientes"
        ]
    },
    
    "planos": {
        "basico": {"nome": "Basico", "preco": "R$ 49,90/mes", "profissionais": "Ate 3"},
        "pro": {"nome": "Pro", "preco": "R$ 89,90/mes", "profissionais": "Ilimitados"},
        "teste": {"nome": "Teste Gratis", "duracao": "7 dias", "plano": "Pro"}
    },
    
    "suporte": {
        "horario": "Seg-Sab 9h-19h",
        "whatsapp": "(47) 99675-9164"
    }
}

# Respostas rapidas otimizadas
QUICK_RESPONSES = {
    # Links diretos
    "/teste": "Teste gratis 7 dias do plano Pro!\n\nAcesse: barber-flow.store/barberflow\n\nNao precisa cartao de credito.",
    
    "/cadastrar": "Cadastre-se agora:\n\nbarber-flow.store/auth?mode=signup\n\nGratuito por 7 dias!",
    
    "/login": "Acesse sua conta:\n\nbarber-flow.store/auth",
    
    "/app": "Acesse o BarberFlow:\n\nbarber-flow.store/barberflow",
    
    "/site": "Site oficial:\n\nbarber-flow.store",
    
    "/manual": "Manual completo:\n\nbarber-flow.store/manual",
    
    # Planos
    "/planos": "*Planos:*\n\nBasico: R$ 49,90/mes\n- 3 profissionais\n- Agendamento online\n\nPro: R$ 89,90/mes\n- Ilimitado\n- Relatorios\n- WhatsApp\n- Notificacoes\n\nTeste gratis: 7 dias Pro",
    
    # Ajuda
    "/ajuda": "Comandos:\n\n/teste - Testar gratis\n/cadastrar - Criar conta\n/login - Minha conta\n/app - Acessar sistema\n/planos - Ver planos\n/como - Como usar\n/problemas - Suporte\n/humano - Atendente",
    
    # Como usar
    "/como": "Como usar o BarberFlow:\n\n1. Crie sua conta (gratuita)\n2. Cadastre servicos e precos\n3. Adicione seus barbeiros\n4. Configure horarios\n5. Compartilhe seu link\n\nClientes agendam 24h!",
    
    # Suporte
    "/problemas": "Descreva seu problema:\n1. O que aconteceu?\n2. Quando?\n3. Print (se possivel)",
    
    "/horarios": f"Suporte: {KNOWLEDGE_BASE['suporte']['horario']}\nWhatsApp: {KNOWLEDGE_BASE['suporte']['whatsapp']}",
    
    "/humano": f"Falar com atendente:\n\nWhatsApp: {KNOWLEDGE_BASE['suporte']['whatsapp']}\nHorario: {KNOWLEDGE_BASE['suporte']['horario']}",
    
    # Recursos
    "/recurso": "*Recursos do BarberFlow:*\n\n- Agenda online 24h\n- App para clientes\n- Relatorios\n- Comissoes\n- WhatsApp automation\n- Assinaturas\n- Estoque\n- Avaliacoes",
    
    "/whatsapp": "Integracao WhatsApp:\n\nEnvia lembretes e confirmacoes automaticamente. Disponivel no plano Pro.",
    
    "/notificacoes": "Notificacoes push:\n\nLembretes 1h antes do horario. Disponivel no plano Pro.",
    
    "/assinaturas": "Assinaturas recorrentes:\n\nCrie planos mensais para clientes. Cobranca via Mercado Pago. Plano Pro."
}

# Respostas para perguntas comuns (a IA vai usar como referencia)
PERGUNTAS_COMUNS = {
    "teste gratis": "O BarberFlow oferece 7 dias de teste gratuito do plano Pro. Acesse barber-flow.store/barberflow e crie sua conta. Nao precisa cartao de credito.",
    
    "como comecar": "Para comecar:\n1. Acesse barber-flow.store/auth?mode=signup\n2. Crie sua conta\n3. Cadastre servicos\n4. Adicione barbeiros\n5. Compartilhe seu link\n\nClientes agendam 24h!",
    
    "preco": "Planos:\n- Basico: R$ 49,90/mes (3 profissionais)\n- Pro: R$ 89,90/mes (ilimitados)\n- Teste gratis: 7 dias Pro",
    
    "cancelar": "Para cancelar, acesse Configuracoes > Plano no painel. Sem multa ou burocracia.",
    
    "sincronizar": "O BarberFlow funciona 100% online. Dados sincronizam automaticamente em todos os dispositivos.",
    
    "app": "O BarberFlow funciona pelo navegador (barber-flow.store/barberflow). Nao precisa instalar nada!"
}
