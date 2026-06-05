# Security Policy

## Reporting a vulnerability

These are educational code samples, not a production service — but if you find a
security issue (for example, a sample that leaks a key pattern, or an unsafe
default), please report it privately:

- Use GitHub's **[Report a vulnerability](../../security/advisories/new)** (Security tab), **or**
- Contact the maintainer through the email on the author's GitHub profile.

Please **do not** open a public issue for security problems. We'll respond as
soon as we can.

## Never commit secrets

Samples use placeholder keys (`your-api-key`) and a `.env.example`. Never put a
real API key, token, or credential in code or commits. If you accidentally
commit a secret, **rotate it immediately** — rotation, not deletion, is the fix.
