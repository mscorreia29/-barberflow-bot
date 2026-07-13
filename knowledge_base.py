# Base de Conhecimento - BarberFlow (v5)
KNOWLEDGE_BASE = {
    "sistema": {
        "nome": "BarberFlow",
        "url_site": "https://barber-flow.store",
        "url_app": "https://barber-flow.store/barberflow",
        "url_cadastro": "https://barber-flow.store/auth?mode=signup",
        "url_login": "https://barber-flow.store/auth",
        "url_manual": "https://barber-flow.store/manual",
    },
    "planos": {
        "basico": {"nome": "Basico", "preco": "R$ 49,90/mes", "profissionais": "Ate 3"},
        "pro": {"nome": "Pro", "preco": "R$ 89,90/mes", "profissionais": "Ilimitados"},
    },
    "suporte": {
        "horario": "Seg-Sab 9h-19h",
        "whatsapp": "(47) 99675-9164"
    }
}

QUICK_RESPONSES = {
    # Saudacao
    "/ola": "Ola! Tudo bem? 😊 Sou do suporte do BarberFlow. Como posso te ajudar?",
    "/obrigado": "De nada! Fico feliz em ajudar! 😄 Qualquer outra duvida, e so mandar!",
    
    # Links
    "/teste": "Teste gratis por 7 dias! Acesso completo ao plano Pro.\n\nApos 7 dias, o acesso e bloqueado e voce escolhe um plano:\n- Basico: R$ 49,90/mes\n- Pro: R$ 89,90/mes\n\nSem cartao. Comece agora:\nbarber-flow.store/barberflow",
    "/cadastrar": "Crie sua conta gratuitamente:\n\nbarber-flow.store/auth?mode=signup\n\nRapido e facil!",
    "/login": "Acesse sua conta:\n\nbarber-flow.store/auth",
    "/app": "Acesse o BarberFlow:\n\nbarber-flow.store/barberflow\n\nFunciona pelo navegador!",
    "/site": "Site oficial:\n\nbarber-flow.store",
    "/manual": "Manual completo:\n\nbarber-flow.store/manual",
    "/compatibilidade": "Funciona em qualquer dispositivo! Celular, tablet ou PC.\n\nbarber-flow.store/barberflow",
    
    # Planos
    "/planos": "Temos 2 opcoes:\n\n*Basico* - R$ 49,90/mes\nAte 3 profissionais\n\n*Pro* - R$ 89,90/mes\nIlimitado + relatorios + WhatsApp\n\nTeste 7 dias gratis!",
    
    # Como funciona
    "/como": "Funciona assim:\n\n1. Cria sua conta (gratuita)\n2. Cadastra servicos e precos\n3. Adiciona barbeiros\n4. Configura horarios\n5. Manda o link pros clientes\n\nEles agendam sozinhos, 24h!",
    
    # Suporte
    "/horarios": "Suporte:\nSeg-Sab 9h-19h\nWhatsApp: (47) 99675-9164",
    "/humano": "Vou te conectar com um atendente:\n\nWhatsApp: (47) 99675-9164\nHorario: Seg-Sab 9h-19h",
    
    # Recursos
    "/recurso": "O BarberFlow tem:\n\n- Agendamento online 24h\n- Notificacoes automaticas\n- Relatorios de faturamento\n- Comissoes dos barbeiros\n- Assinaturas recorrentes\n- Controle de estoque\n- Avaliacoes de clientes",
    "/whatsapp": "Integracao WhatsApp:\nEnvia lembretes e confirmacoes automaticamente. Plano Pro!",
    "/notificacoes": "Notificacoes push:\nClientes recebem lembrete 1h antes. Plano Pro.",
    "/assinaturas": "Assinaturas recorrentes:\nPlanos mensais automaticos via Mercado Pago. Plano Pro.",
    
    # Compartilhar
    "/compartilhar": "Para compartilhar:\n1. Acesse barber-flow.store/barberflow\n2. Va em Configuracoes > Link de Agendamento\n3. Copie e envie pros clientes!",
    
    # Cancelar
    "/cancelar": "Para cancelar:\nConfiguracoes > Plano no painel.\nSem multa!",
    
    # Sugestoes
    "/sugestao": "Obrigado! Vou registrar no backlog. Sua opiniao e valiosa!",
    "/feedback": "Obrigado! Vou registrar no backlog!",
    
    # Barbeiro
    "/barbeiro": "Para vincular:\n1. Acesse barber-flow.store/barberflow\n2. Barbeiros > Novo Barbeiro\n3. Preencha e salve\n\nAcesso gerado na hora! Copia e manda pelo WhatsApp!",
    
    # === COBRANCAS ===
    "/lembrete_vencimento": "Olá {name}! Sua assinatura do BarberFlow ({plan}) vence em {days} dia(s). Renove em barber-flow.store/auth para continuar usando!",
    "/confirmacao_pagamento": "Pagamento confirmado! ✅ Sua assinatura do BarberFlow ({plan}) foi renovada. Obrigado!",
    "/cobranca_pendente": "Olá {name}! Identificamos que seu pagamento do plano {plan} (R$ {price}) ainda nao foi processado. Acesse barber-flow.store/auth para regularizar.",
    "/pix_pagamento": "Para pagar seu plano {plan} (R$ {price}), acesse:\n\nbarber-flow.store/auth?mode=signup\n\nOu pague via PIX:\nChave: {pix_key}",
    "/relatorio_mensal": "📊 Relatório Mensal BarberFlow\n\nPeriodo: {month}\nPlano: {plan}\nStatus: {status}\nProximo vencimento: {next_date}",
    
    # === AGENDAMENTO ===
    "/agendar": "Para agendar um horario:\n\n1. Acesse barber-flow.store/barberflow\n2. Va em Agenda > Novo Agendamento\n3. Escolha o cliente, barbeiro e horario\n\nOu me envie: data, horario e nome do barbeiro!",
    "/ver_agenda": "Para ver sua agenda:\n\nAcesse barber-flow.store/barberflow > Agenda\n\nOu me envie a data que quero consultar!",
    
    # === MARKETING ===
    "/promocao": "Tem alguma promocao pra divulgar? Me envie os detalhes e posso ajudar a criar uma campanha!",
}

SAUDACOES = ["oi", "ola", "bom dia", "boa tarde", "boa noite", "e ai", "fala", "hello", "hi", "hey", "eae"]

PERGUNTAS_COMUNS = {
    "teste gratis": "Teste 7 dias do plano Pro, sem cartao. Acesse barber-flow.store/barberflow!",
    "como comecar": "Crie sua conta, cadastre servicos, barbeiros e compartilhe o link!",
    "preco": "Basico: R$ 49,90/mes. Pro: R$ 89,90/mes. Teste 7 dias gratis!",
    "cancelar": "Configuracoes > Plano. Sem multa!",
    "barbeiro": "Barbeiros > Novo Barbeiro. Acesso copiado pelo WhatsApp!",
    "comissao": "Calcula comissao automatico! Plano Pro.",
    "mercado pago": "Assinaturas via Mercado Pago. Plano Pro.",
    "relatorio": "Dashboard com faturamento e comissoes. Plano Pro.",
    "estoque": "Controle de estoque nos dois planos!",
    "avaliacao": "Clientes avaliam no app. Dois planos!",
    "compartilhar": "Configuracoes > Link de Agendamento!",
    "agendar": "Acesse barber-flow.store/barberflow > Agenda. Me envie data e horario!",
    "pagamento": "Acesse barber-flow.store/auth para verificar status do pagamento.",
    "vencimento": "Sua assinatura vence em breve? Renove em barber-flow.store/auth!",
}
