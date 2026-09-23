# Citizen Contribution Moderation & Verification Guidelines
**Role:** Member 8 (Community & Verification)
**Coverage:** My Ekiti Story & Ekiti 2056

## 1. Lifecycle States
- **PENDING_MODERATION:** Default intake state upon user submission via `POST /api/v1/contributions/submit`.
- **MODERATED:** Passed safety checks (no spam, hate speech, or inappropriate media).
- **VERIFIED:** Factual assertions checked or marked with proper attribution flags.
- **PUBLISHED:** Approved for public display on the platform.
- **REJECTED:** Violates community policies or safety standards.

## 2. Moderation Checklist (Stage 1)
- **Safety:** Check for hate speech, harassment, spam, advertising, or inappropriate content.
- **Privacy:** Ensure no personal phone numbers, home addresses, or sensitive credentials are included.
- **LGA Verification:** Confirm the selected LGA matches one of the official 16 Ekiti LGAs.

## 3. Fact & Classification Standards (Stage 2 & 3)
- **Personal Stories (My Ekiti Story):** Mark as `is_community_claim = true`. Stories reflect personal/oral memory; do not inject into the RAG Knowledge Base vector database.
- **Future Visions (Ekiti 2056):** Treat as viewpoints/opinions (`OPINION/VISION`). Verification of historical facts is not required for future aspirations.
- **Historical Claims:** If a submission makes a formal historical claim, cross-reference against Level 1/Level 2 authoritative sources before marking as `VERIFIED`.

## 4. Editorial Review
- Edits must preserve original meaning while improving grammar or clarity where required.
- Escalation: Historical disputes -> Research Team; Cultural/Tourism queries -> Culture & Tourism Team; Yoruba language context -> Project Lead.
