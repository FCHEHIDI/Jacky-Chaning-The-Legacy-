# CLAUDE.md — Project Brain
> Relu à chaque session. Rester concis — chaque token compte.

## État courant

```
PHASE ACTIVE : MAP (phase 2)
FICHIER ACTIF : src/app.py
DERNIÈRE DÉCISION : survey terminé — 17 smells catalogués (8 critiques), gate ouverte
PROCHAIN OBJECTIF : cartographier les dépendances et zones de risque
```

> Mettre à jour ce bloc via `/compact` à chaque changement de phase.

---

## Règles absolues

1. **Jamais modifier `src/`** avant `/stabilize` complété (tous les tests verts)
2. **Jamais passer à la phase N+1** sans `python scripts/check_gate.py <phase>` → exit 0
3. **Jamais de SQL brut** dans le code cible — SQLAlchemy ORM uniquement
4. **Jamais MD5/SHA1** pour les passwords — bcrypt uniquement
5. **Jamais `except:`** nu — exceptions spécifiques uniquement
6. **Jamais de secrets hardcodés** — variables d'env via `config.py`
7. **Jamais `print()`** comme logging — structlog uniquement

---

## Contexte d'injection (ordre strict — lire AVANT toute réponse)

```
OBLIGATOIRE :
1. CLAUDE.md              ← ce fichier
2. session/context.yaml   ← état compact depuis SQLite (~164 tokens)
3. prompts/system.md      ← persona + contraintes

CONDITIONNEL par phase :
/survey /stabilize        → src/app.py
/draft /derive            → prompts/conventions.md + prompts/data_contract.md
/derive                   → prompts/coding_standards.md + logs/audit/latest.md
reprise in_progress       → session/history.md
```

> `context.yaml` est auto-généré via `python scripts/state.py export yaml`. Ne pas éditer manuellement.

---

## Phases

```
[1] /survey     → inventaire brut + cataloguer smells dans state.db
[2] /map        → carte dépendances + zones rouge/orange/vert
[3] /audit      → scoring OWASP + qualité + maintenabilité
[4] /draft      → plan d'intervention + contrats d'interface
[5] /stabilize  → tests pytest qui figent le comportement legacy
[6] /derive     → refacto module par module (gate: pytest + mypy + coverage ≥ 80%)
[7] /extend     → nouvelles features post-refacto
```

Transversales : `/compact` (compression session) · `/doctor` (diagnostic blockers)

---

## Tooling

```bash
make help                              # toutes les commandes disponibles
make status                            # phase courante + résumé
make smells                            # smells open
make gate-<phase>                      # valider critères de sortie
make dump                              # export SQL + YAML (à committer)
make test                              # pytest
make check                             # lint + mypy
```

---

## Architecture cible

```
src/app.py → create_app() seulement
src/config.py · src/db.py
src/models/    user · project · task · comment  (SQLAlchemy)
src/schemas/   user · project · task            (Pydantic)
src/routes/    auth · projects · tasks · admin  (Blueprints)
src/services/  auth · task · project            (logique métier)
src/utils/     logger · security
tests/         conftest · test_auth · test_tasks · test_projects · test_admin
```

---

## Décisions prises

> Toutes les décisions sont dans `state.db`. Consulter via `make decisions`.
> Ce tableau est intentionnellement vide pour préserver le budget tokens de CLAUDE.md.

