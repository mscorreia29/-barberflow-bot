# Base de Conhecimento - BarberFlow (v3)
# Respostas naturais e conversacionais

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

QUICK_RESPONSES = {
    # Saudacao
    "/ola": "Ola! Tudo bem? 😊 Sou do suporte do BarberFlow. Como posso te ajudar?",
    
    # Links diretos - tom mais natural
    "/teste": "Teste gratis por 7 dias! Acesso completo ao plano Pro.\n\nApos 7 dias, o acesso e bloqueado e voce escolhe um plano pra continuar:\n- Basico: R$ 49,90/mes\n- Pro: R$ 89,90/mes\n\nSem cartao de credito. Comece agora:\nbarber-flow.store/barberflow",
    
    "/cadastrar": "Crie sua conta gratuitamente:\n\nbarber-flow.store/auth?mode=signup\n\nRapido e facil! Precisa de ajuda com algo?",
    
    "/login": "Pra acessar sua conta:\n\nbarber-flow.store/auth\n\nEsqueceu a senha? La tem a opcao de recuperar!",
    
    "/app": "Acesse o BarberFlow aqui:\n\nbarber-flow.store/barberflow\n\nFunciona pelo celular e computador, sem precisar instalar nada!",
    
    "/site": "Site oficial:\n\nbarber-flow.store\n\nLa voce encontra todas as informacoes!",
    
    "/manual": "Tem todo o passo a passo aqui:\n\nbarber-flow.store/manual\n\nSe tiver duvida em algo especifico, me fala que te ajudo!",
    
    # Planos - conversacional
    "/planos": "Temos 2 opcoes:\n\n*Basico* - R$ 49,90/mes\nAte 3 profissionais\n\n*Pro* - R$ 89,90/mes\nIlimitado + relatorios + WhatsApp\n\nTeste 7 dias gratis antes de decidir!",
    
    # Como funciona - passo a passo natural
    "/como": "Funciona assim:\n\n1. Cria sua conta (gratuita)\n2. Cadastra seus servicos\n3. Adiciona os barbeiros\n4. Configura os horarios\n5. Manda o link pros clientes\n\nPronto! Eles agendam sozinhos, 24h! 😄",
    
    # Suporte
    "/problemas": "Me conta o que aconteceu:\n\n1. Qual o problema?\n2. Quando comecou?\n3. Consegue mandar um print?\n\nAssim consigo te ajudar melhor!",
    
    "/horarios": "Suporte:\nSeg-Sab das 9h as 19h\nWhatsApp: (47) 99675-9164",
    
    "/humano": "Vou te conectar com um atendente:\n\nWhatsApp: (47) 99675-9164\nHorario: Seg-Sab 9h-19h\n\nEle vai te atender rapidinho!",
    
    # Recursos - beneficios
    "/recurso": "O BarberFlow tem tudo que sua barbearia precisa:\n\n- Agendamento online 24h\n- Notificacoes automaticas\n- Relatorios de faturamento\n- Comissoes dos barbeiros\n- Assinaturas recorrentes\n\nQuer saber mais sobre algum?",
    
    "/whatsapp": "Integracao com WhatsApp:\n\nManda lembretes e confirmacoes automaticamente pros clientes. No plano Pro!",
    
    "/notificacoes": "Notificacoes push:\n\nClientes recebem lembrete 1h antes do horario. Elimina faltas! Plano Pro.",
    
    "/assinaturas": "Assinaturas recorrentes:\n\nCria planos mensais pros seus clientes. Cobranca automatica via Mercado Pago. Plano Pro.",
    
    # Cancelar
    "/cancelar": "Para cancelar, va em Configuracoes > Plano no painel.\n\nSem multa, sem burocracia. Mas antes, me conta o que aconteceu? Talvez eu possa ajudar!",
    
    # Sugestoes/Melhorias
    "/sugestao": "Obrigado pela sugestao! Vou registrar no nosso backlog pra equipe avaliar.\n\nSua opniao e muito importante pra gente melhorar o BarberFlow! 😄",
    
    "/feedback": "Obrigado pelo feedback! Vou registrar no nosso backlog pra equipe avaliar.\n\nSua opniao e muito importante pra gente melhorar o BarberFlow! 😄",
}

# Saudacoes
SAUDACOES = ["oi", "ola", "bom dia", "boa tarde", "boa noite", "e ai", "fala", "hello", "hi", "hey", "bom dia", "boa tarde", "boa noite"]

PERGUNTAS_COMUNS = {
    "teste gratis": "Teste 7 dias do plano Pro, sem cartao de credito. Acesse barber-flow.store/barberflow e crie sua conta!",
    
    "como comecar": "E bem facil!\n1. Crie sua conta em barber-flow.store/auth?mode=signup\n2. Cadastre seus servicos\n3. Adicione os barbeiros\n4. Compartilhe o link\n\nPronto, clientes agendam 24h!",
    
    "preco": "Temos 2 planos:\n- Basico: R$ 49,90/mes (3 profissionais)\n- Pro: R$ 89,90/mes (ilimitados)\n\nTeste 7 dias gratis antes!",
    
    "cancelar": "Sem problemas! Va em Configuracoes > Plano e cancele. Sem multa. Mas me conta, algo te desagradou?",
    
    "sincronizar": "O BarberFlow funciona 100% online! Seus dados atualizam automaticamente no celular e computador.",
    
    "app": "Funciona pelo navegador, sem instalar nada! Acesse barber-flow.store/barberflow\n\nFunciona em qualquer celular ou PC!",
    
    "quanto custa": "O basico comeca em R$ 49,90/mes. Teste gratis por 7 dias primeiro!",
    
    "barbeiro": "Voce pode adicionar quantos barbeiros quiser no plano Pro! No basico sao 3. Cadastre em barber-flow.store/barberflow",
    
    "agendamento": "Clientes agendam 24h pelo link que voce compartilhar. Funciona automatico!",
    
    "comissao": "O sistema calcula comissao dos barbeiros automatico! Plano Pro."
}
