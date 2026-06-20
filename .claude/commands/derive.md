# /derive — Refacto incrémental, module par module

Argument requis : `/derive <module>` (ex: `/derive auth`, `/derive tasks`)

## Initialisation
```bash
python scripts/state.py log INFO "Starting /derive <module>" derive
```

Lis dans cet ordre :
1. `session/context.yaml`
2. `logs/audit/latest.md`
3. `logs/audit/draft.md`
4. `prompts/conventions.md`
5. `prompts/coding_standards.md`
6. `prompts/data_contract.md`

Puis lis le code du module correspondant dans `src/app.py`.

## Procédure pour chaque module

### Étape 1 — Audit ciblé
Lance mentalement `/audit <module>` sur le code source.
Document les risques spécifiques à cette migration.

### Étape 2 — Créer le fichier cible
Crée le fichier dans l'architecture cible (ex: `src/routes/auth.py`, `src/services/auth_service.py`).
Respects scrupuleusement : conventions, contrats d'interface, coding_standards.

### Étape 3 — Migrer sans casser
- SQLAlchemy ORM (pas de SQL brut)
- bcrypt (pas MD5)
- Pydantic pour les inputs
- structlog (pas de print)
- Enum ou constantes (pas de magic strings)
- Type hints complets
- Gestion d'erreurs explicite

### Étape 4 — Marquer les smells corrigés
Pour chaque smell fixé dans ce module :
```bash
python scripts/state.py smell fix <id> derive
python scripts/state.py decision add derive "<ce qui a changé>" "<pourquoi>"
```

### Étape 5 — Valider
```bash
python -m pytest tests/ -v
python -m mypy src/ --strict --ignore-missing-imports
python scripts/check_gate.py derive
```

### Étape 6 — Logger et métriques
```bash
python scripts/state.py metric record derive modules_migrated <N>
python scripts/state.py log DONE "Module <module> migré" derive
```
Ecris un log dans `logs/refactor/<module>.md`.

Mets à jour `CLAUDE.md` — bloc "État courant".
Quand tous les modules sont migrés, lance `python scripts/check_gate.py derive` puis propose `/extend`.
1. `session/context.md`
2. `logs/audit/latest.md`
3. `logs/audit/draft.md`
4. `prompts/conventions.md`
5. `prompts/coding_standards.md`
6. `prompts/data_contract.md`

Puis lis le fichier legacy correspondant au module demandé dans `src/app.py`.

## Procédure pour chaque module

### Étape 1 — Audit ciblé
Lance mentalement `/audit <module>` sur le code source du module.
Document les risques spécifiques à cette migration.

### Étape 2 — Créer le fichier cible
Crée le fichier dans l'architecture cible (ex: `src/routes/auth.py`, `src/services/auth_service.py`).
Respects scrupuleusement :
- Les conventions de `prompts/conventions.md`
- Les contrats d'interface de `prompts/data_contract.md`
- Les standards de `prompts/coding_standards.md`

### Étape 3 — Migrer sans casser
- Utilise SQLAlchemy ORM (pas de SQL brut)
- Utilise bcrypt (pas MD5)
- Valide les inputs avec Pydantic
- Remplace les print() par structlog
- Élimine les magic strings (utilise des Enum ou constantes)
- Type hints sur toutes les fonctions publiques
- Gestion d'erreurs explicite (pas de bare except)

### Étape 4 — Tests
Vérifie que les tests de `/stabilize` passent toujours.
Ajoute des tests unitaires pour le nouveau module dans `tests/`.

### Étape 5 — Logger
Écris un log de migration dans `logs/refactor/<module>.md` :
- Smells corrigés
- Décisions prises
- Comportement préservé
- Breaking changes éventuels

Mets à jour `CLAUDE.md` — bloc "État courant" + "Décisions prises".
Quand tous les modules sont migrés, propose `/extend`.
