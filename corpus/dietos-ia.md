# DietOS — geração de dieta com IA

O DietOS gera plano alimentar a partir de dados clínicos estruturados.

Como funciona:

- O app monta o payload. A geração roda no backend.
- O servidor sanitiza o input e chama o Gemini, com fallback Groq se configurado.
- Há rate limit específico, limite do plano gratuito e regeneração só para Premium.
- A chave da API não fica no cliente.

Isto **não é RAG**. O modelo recebe um payload, não um índice de PDFs. Dado clínico de registro permanece no banco, não num vector store.

RAG só faria sentido para documentos (protocolo nutricional, FAQ interno), com dono do texto e recusa quando o trecho não existe.
