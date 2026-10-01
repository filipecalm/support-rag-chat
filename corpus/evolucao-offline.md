# Evolução offline

O profissional registra as informações. Sem internet durante o registro das informações, o fluxo continua.

Regra do processo:

1. Gravar localmente.
2. Entrar na fila.
3. Sincronizar com a API quando a rede voltar.
4. Só sair da fila depois da confirmação do servidor, para não duplicar.
5. Manter autenticação e vínculo com o paciente certo.

Resultado esperado: o atendimento não trava por falta de rede.

Isto é automação de processo no produto (fila, idempotência). Não é RPA de tela. Se o sistema tem API, não começar por robô de clique.
