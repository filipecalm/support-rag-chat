# Premium payments — checkout and webhook

Premium access must not depend only on a “payment successful” screen.

Flow:

1. The backend creates a checkout session.
2. The user pays through the provider.
3. A signed webhook updates the entitlement in the database.
4. The app checks the status.

Rules:

- The secret key never goes to the client.
- Test and live environments must not be mixed.
- Each webhook endpoint has its own secret.

This is event-driven integration (functionally similar to an n8n/Make connector). Do not claim n8n is used in production just because the pattern is similar.
