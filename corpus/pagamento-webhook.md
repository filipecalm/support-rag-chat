# Pagamento Premium — checkout e webhook

O Premium não pode depender só da tela “pagamento ok”.

Fluxo:

1. O backend cria a sessão de checkout.
2. O usuário paga no provedor.
3. O webhook assinado atualiza o direito no banco.
4. O app consulta o status.

Regras:

- A chave secreta não vai para o cliente.
- Teste e live não se misturam.
- Cada endpoint de webhook tem o secret dele.

Isto é integração por evento (o equivalente funcional de n8n/Make com conector). Não afirmar n8n em produção só porque o padrão é o mesmo.
