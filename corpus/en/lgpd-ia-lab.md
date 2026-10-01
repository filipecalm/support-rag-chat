# Data protection and AI (lab policy)

Do not send medical records, direct patient identifiers, payment tokens, or production secrets to a model or RAG index.

Allowed in this lab's knowledge base: processes, rules, runbooks, and internal FAQs without personal data.

Clinical data, permissions, and billing stay in the system of record.

If retrieval finds no passage above the minimum score, the correct response is to refuse. Filling gaps with general model knowledge in a clinical or financial workflow is a failure, not a feature.

Every document must have an owner. An ownerless corpus becomes a stale wiki and an expensive source of hallucinations.
