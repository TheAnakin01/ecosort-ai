# Security and Privacy Requirements

## 1. Data protection principles

- Collect the minimum data needed for a scan.
- Do not store uploaded images by default.
- Do not request account, contacts or location permissions for the basic scan flow.
- Explain why camera and photo-library access are needed.
- Avoid analytics or tracking until separately approved.
- Keep all secrets out of source control and mobile bundles.

## 2. Image upload security

- Enforce upload byte-size limits.
- Verify actual decoded file format.
- Restrict formats to those the backend supports.
- Limit image pixel dimensions and guard against decompression bombs.
- Use safe temporary-file handling if disk storage is unavoidable.
- Delete temporary files after inference.
- Do not execute or trust metadata embedded in images.
- Do not log image contents or persistent public URLs.

## 3. API security

- Use HTTPS in deployed environments.
- Apply rate limits appropriate to the deployment.
- Set request timeouts and resource limits.
- Restrict CORS.
- Return safe error messages.
- Add request IDs for diagnostics.
- Consider abuse protection before public launch.
- Keep model and server administration endpoints private.

## 4. Secrets management

Examples of secrets/configuration:
- Supabase service-role key.
- Database password.
- Hosting credentials.
- Any external API token.

Rules:
- Store backend secrets in deployment environment variables or secret manager.
- Commit only `.env.example` with placeholder values.
- Never place a service-role key in Expo app configuration or client code.
- If a secret is accidentally committed, rotate it immediately. Deleting the file in a later commit does not remove it from Git history.

## 5. User data

If accounts/history are later added:
- Obtain clear consent and explain stored fields.
- Use Row Level Security.
- Allow users to delete their history.
- Define retention and account deletion behavior.
- Avoid precise geolocation unless necessary and approved.
- Do not use images or feedback for model training without clear disclosure and consent.

## 6. Threat considerations

| Threat | Mitigation |
|---|---|
| Oversized/malicious image | Byte and pixel limits, safe decoder, timeouts |
| API abuse | Rate limits, request limits, monitoring |
| Secret exposure | Environment secrets, Git ignore, rotation |
| Cross-user data access | RLS and authorization tests |
| Accidental image retention | Stateless inference, temporary cleanup |
| Misleading output | Confidence qualification and limitation copy |
| Dependency vulnerability | Pinned dependencies and periodic review |

## 7. Privacy checklist before release

- [ ] No secrets in repository or app bundle.
- [ ] No raw image retention by default.
- [ ] Camera/gallery permission copy is clear.
- [ ] Logs exclude image content and sensitive data.
- [ ] Upload validation and limits are tested.
- [ ] HTTPS is enabled in production.
- [ ] Database RLS is tested if database is enabled.
- [ ] Privacy notice matches actual behavior.
