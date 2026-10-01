# LGPD e IA (política de lab)

Não enviar prontuário, identificador direto de paciente, token de pagamento ou segredo de produção para modelo ou índice de RAG.

O que pode ir para a base de conhecimento deste lab: processo, regra, runbook, FAQ interno sem dado pessoal.

O que fica no sistema de registro: clínico, permissão, fatura.

Se o retrieval não achar trecho com score mínimo, a resposta correta é recusar. Completar com “conhecimento geral” do modelo em processo clínico ou financeiro é falha, não feature.

Dono do documento tem que existir. Corpus sem dono vira wiki morta e alucinação cara.
