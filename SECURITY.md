# Security policy

## Reporting vulnerabilities

Email: `security@pypemesh.dev` (placeholder until commercial entity formed).
For now, open a **private security advisory** on GitHub.

Please include:
- Description
- Reproduction steps
- Affected version(s)
- Potential impact

We respond within 72 hours and aim to patch within 14 days for critical
issues.

## Scope

- `pypemesh-core`: solver, parsers, any user-data input handling
- `pypemesh-web/backend`: API, authentication, file upload, solver execution
- `pypemesh-web/frontend`: XSS, CSRF, client-side data handling

## Out of scope

- Engineering correctness disputes — these go in regular issues
- Third-party dependency CVEs we can't patch directly — please ping upstream
- Rate limiting on our hosted instance — known limitation pre-v1.0

## Disclosure

Coordinated. We credit reporters in the security advisory unless anonymity
requested.
