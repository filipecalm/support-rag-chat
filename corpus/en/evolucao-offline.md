# Offline progress notes (home care)

A professional records a progress note at a patient's home. The network often drops, but the workflow must continue without internet.

Process rules:

1. Save locally.
2. Add the note to a queue.
3. Sync with the API when the network returns.
4. Remove it from the queue only after server confirmation, to prevent duplicates.
5. Preserve authentication and the link to the correct patient.

Expected result: care is not blocked by a network outage.

This is product workflow automation (queue and idempotency), not screen-based RPA. If the system has an API, do not start with a click bot.
