# /extend — Ajout de nouvelles capacités post-refacto

⚠️ Cette phase ne doit être atteinte qu'après `/derive` complet et tous les tests au vert.

Lis :
1. `session/context.md`
2. `session/history.md`
3. `prompts/conventions.md`
4. `prompts/coding_standards.md`

Argument optionnel : `/extend <feature>` pour une feature spécifique.
Sans argument : propose une liste de features candidates.

## Features candidates (à prioriser avec l'utilisateur)

### Sécurité
- Rate limiting sur `/login` (Flask-Limiter)
- JWT tokens (remplace sessions cookie)
- Refresh token rotation
- Audit log des actions admin

### Qualité API
- Pagination sur GET /tasks et GET /projects
- Filtres avancés (date range, multi-status)
- Versionning d'API (/api/v1/)
- OpenAPI/Swagger auto-généré

### Observabilité
- Health check endpoint `/health`
- Métriques Prometheus `/metrics`
- Structlog avec correlation ID par requête
- Sentry integration pour les erreurs

### Developer Experience
- Docker Compose (app + DB)
- Makefile avec targets : test, lint, run, migrate
- Pre-commit hooks (ruff, mypy)
- CI GitHub Actions

## Procédure
Pour chaque feature :
1. Définis le contrat d'interface dans `prompts/data_contract.md`
2. Écris le test en premier (TDD)
3. Implémente
4. Vérifie que les tests existants passent encore
5. Documente dans `logs/refactor/extensions.md`

Mets à jour `CLAUDE.md` — bloc "Décisions prises".
