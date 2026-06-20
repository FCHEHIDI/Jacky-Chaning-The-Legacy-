# /stabilize — Tests qui figent le comportement actuel

⚠️ RÈGLE CRITIQUE : Ne modifier AUCUN fichier de `src/` pendant cette phase.
L'objectif est de créer un filet de sécurité AVANT tout refacto.

## Initialisation
```bash
python scripts/state.py phase set stabilize in_progress
```

Lis :
1. `session/context.yaml`
2. `logs/audit/draft.md`
3. `src/app.py` en entier

Génère les fichiers de test suivants (pytest) :

### `tests/conftest.py`
- Fixture `app` : Flask test client avec DB SQLite en mémoire
- Fixture `client` : client HTTP de test
- Fixture `auth_client` : client déjà authentifié
- Fixture `admin_client` : client authentifié avec rôle admin
- Helper pour créer des projets/tâches de test

### `tests/test_auth.py`
- Test register : succès, doublon, champs manquants
- Test login : succès, mauvais mot de passe, utilisateur inexistant
- Test logout : session effacée
- Test accès sans auth : retourne 401

### `tests/test_projects.py`
- Test GET /projects : liste vide, liste avec données
- Test POST /projects : succès, doublon, sans auth
- Test DELETE /projects/<id> : admin OK, user interdit, projet inexistant

### `tests/test_tasks.py`
- Test GET /tasks : filtre par project_id, par status, par assigned_to
- Test POST /tasks : succès, projet inexistant, titre vide
- Test PUT /tasks/<id> : mise à jour partielle, aucun champ fourni
- Test DELETE /tasks/<id> : supprime aussi les commentaires

### `tests/test_admin.py`
- Test GET /admin/users : accessible sans auth (bug documenté)
- Test POST /admin/reset : accessible sans auth (bug documenté)
- Test GET /stats : métriques correctes, cas division par zéro
- Test GET /search : injection SQL safe après refacto
- Test GET /export : fichier créé

## Validation
Après génération des tests, exécute :
```bash
python -m pytest tests/ -v
```
Tous les tests DOIVENT passer sur le code legacy.
Enregistre les métriques :
```bash
python scripts/state.py metric record stabilize tests_total <N>
python scripts/state.py metric record stabilize tests_passing <N>
```
Vérifie la gate :
```bash
python scripts/check_gate.py stabilize
```
Si la gate est ouverte :
```bash
python scripts/state.py phase set stabilize completed
```
Mets à jour `CLAUDE.md` — bloc "État courant".
Propose ensuite `/derive`.
1. `session/context.md`
2. `logs/audit/draft.md`
3. `src/app.py` en entier

Génère les fichiers de test suivants (pytest) :

### `tests/conftest.py`
- Fixture `app` : Flask test client avec DB SQLite en mémoire
- Fixture `client` : client HTTP de test
- Fixture `auth_client` : client déjà authentifié
- Fixture `admin_client` : client authentifié avec rôle admin
- Helper pour créer des projets/tâches de test

### `tests/test_auth.py`
- Test register : succès, doublon, champs manquants
- Test login : succès, mauvais mot de passe, utilisateur inexistant
- Test logout : session effacée
- Test accès sans auth : retourne 401

### `tests/test_projects.py`
- Test GET /projects : liste vide, liste avec données
- Test POST /projects : succès, doublon, sans auth
- Test DELETE /projects/<id> : admin OK, user interdit, projet inexistant

### `tests/test_tasks.py`
- Test GET /tasks : filtre par project_id, par status, par assigned_to
- Test POST /tasks : succès, projet inexistant, titre vide
- Test PUT /tasks/<id> : mise à jour partielle, aucun champ fourni
- Test DELETE /tasks/<id> : supprime aussi les commentaires

### `tests/test_admin.py`
- Test GET /admin/users : accessible sans auth (bug documenté)
- Test POST /admin/reset : accessible sans auth (bug documenté)
- Test GET /stats : métriques correctes, cas division par zéro
- Test GET /search : injection SQL safe après refacto
- Test GET /export : fichier créé

Ces tests doivent PASSER sur le code legacy actuel pour valider qu'ils capturent le comportement existant.
Mets à jour `CLAUDE.md` — bloc "État courant".
Propose ensuite `/derive`.
