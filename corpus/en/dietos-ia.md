# DietOS — AI-generated meal plans

DietOS generates meal plans from structured clinical data.

How it works:

- The app builds the payload. Generation runs on the backend.
- The server sanitizes input and calls Gemini, with a Groq fallback if configured.
- There is a specific rate limit, a free-plan limit, and regeneration is Premium-only.
- The API key never reaches the client.

This is **not RAG**. The model receives a payload, not a PDF index. Clinical record data stays in the database, not in a vector store.

RAG would make sense only for documents (nutrition protocols, internal FAQs), with a document owner and refusal when the relevant passage is missing.
