# Open Questions and Decisions Requiring Confirmation

The agent should not block core development on every question. Use the proposed defaults below, record assumptions and ask the product owner when a decision materially affects implementation.

| Topic | Proposed default | When confirmation is required |
|---|---|---|
| Mobile framework | React Native + Expo + TypeScript | Before replacing with another framework |
| First platform | Android-first | Before iOS-specific release commitments |
| Detection classes | paper, plastic, metal, organic | Before adding/removing classes |
| Model | pretrained YOLO nano detector, fine-tuned | Before switching model family |
| Inference location | Backend | Before adding on-device inference |
| Backend | FastAPI | Before replacing API stack |
| Database | None for scan-only MVP; Supabase later | Before adding auth/history/persistence |
| Image retention | No raw image storage by default | Before storing uploads or using them for training |
| History | Excluded from core MVP | Before implementing local/cloud history |
| Localization | English first | Before adding language requirements |
| Disposal guidance | General cautious rules, not location-specific | Before publishing local municipal guidance |
| App theme | Clean nature-inspired utility UI | Before locking a full brand system |
| Deployment host | Select after model resource measurement | Before committing to a provider |
| Model confidence threshold | Tune on validation set | Before claiming a threshold is final |

## Questions for product owner

1. What is the final app name and brand identity?
2. Should history be local-only in the first public demo, or excluded entirely?
3. Is the first target specifically Mumbai/Maharashtra disposal guidance, or general India guidance? Any local guidance must be verified from authoritative municipal sources.
4. Which Android versions/devices should be supported?
5. What is the expected demo environment: local laptop backend, public hosted backend, or both?
6. Is there a preferred dataset budget or annotation platform?
7. What is the desired language for the first release?

## Decision log template

For each approved change, record:
- Date.
- Decision.
- Reason.
- Alternatives considered.
- Documents/code affected.
- Whether migration or backward compatibility is needed.
