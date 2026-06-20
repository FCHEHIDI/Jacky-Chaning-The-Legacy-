# Survey — Inventaire brut du legacy
> Généré le 2026-06-20 | Phase 1 / 7

---

## 1. Métriques brutes

| Métrique | Valeur |
|---|---|
| Lignes totales | 368 |
| Lignes de code effectif | ~280 |
| Fonctions / handlers | 15 (init_db + 14 routes) |
| Routes HTTP | 17 endpoints |
| Tables DB | 4 |
| Fichiers source | 1 (monolithique) |

### Imports utilisés
```python
from flask import Flask, request, jsonify, session
import sqlite3
import hashlib
import os        # importé mais INUTILISÉ
import json
import datetime
```
> `os` est importé sans être utilisé nulle part.

### Tables et relations
```
users       (id PK, username, password TEXT, role, created_at)
projects    (id PK, name, owner TEXT, status, budget REAL, created_at)
tasks       (id PK, title, description, project_id INT, assigned_to TEXT,
             status, priority INT, due_date TEXT, created_at, tags TEXT/JSON)
comments    (id PK, task_id INT, author TEXT, body, created_at)
```
Relations implicites (aucune FOREIGN KEY déclarée) :
- `tasks.project_id` → `projects.id`
- `comments.task_id` → `tasks.id`
- `tasks.assigned_to` → `users.username` (texte libre, pas de FK)
- `projects.owner` → `users.username` (texte libre, pas de FK)

### Dépendances externes
| Package | Rôle | Version |
|---|---|---|
| Flask | Web framework | non épinglé |
| sqlite3 | DB (stdlib) | intégré Python |
| hashlib | Hachage MD5 | intégré Python |

---

## 2. Inventaire des routes

| # | Méthode | Chemin | Auth | Opérations DB | Retour |
|---|---|---|---|---|---|
| 1 | POST | /register | Aucune | INSERT users | `{status, user}` / 400 |
| 2 | POST | /login | Aucune | SELECT users | `{status, role}` / 401 |
| 3 | GET | /logout | Aucune | Aucune | `{status}` |
| 4 | GET | /projects | session | SELECT projects | `[project...]` |
| 5 | POST | /projects | session | SELECT+INSERT projects | `{status, name}` |
| 6 | DELETE | /projects/\<id\> | session+admin | DELETE tasks+projects | `{status}` |
| 7 | GET | /tasks | session | SELECT tasks (filtres) | `[task...]` |
| 8 | POST | /tasks | session | SELECT+INSERT tasks | `{status, title}` |
| 9 | PUT | /tasks/\<id\> | session | UPDATE tasks | `{status}` |
| 10 | DELETE | /tasks/\<id\> | session | DELETE comments+tasks | `{status}` |
| 11 | GET | /tasks/\<id\>/comments | **AUCUNE** | SELECT comments | `[comment...]` |
| 12 | POST | /tasks/\<id\>/comments | session | INSERT comments | `{status}` |
| 13 | GET | /stats | session | 5x SELECT COUNT + SELECT tasks | `{stats...}` |
| 14 | GET | /search | session | SELECT tasks+projects LIKE | `{tasks, projects}` |
| 15 | GET | /admin/users | **AUCUNE** | SELECT users | `[user...]` |
| 16 | POST | /admin/reset | **AUCUNE** | DELETE tasks+projects+comments | `{status}` |
| 17 | GET | /export | session | SELECT tasks+projects | `{status, file}` → écrit disque |

---

## 3. Catalogue des smells

### SECURITE

#### S1 — SQL Injection généralisée 🔴 Critique
- **Localisation :** `register()` l.74, `login()` l.88, `create_project()` l.135/138, `delete_project()` l.150/151, `get_tasks()` l.167–173, `create_task()` l.210/214–215, `update_task()` l.231–245, `delete_task()` l.255–256, `get_comments()` l.265, `add_comment()` l.277, `search()` l.318–322
- **Description :** Concaténation directe de paramètres utilisateur dans des requêtes SQL. Toutes les routes construisent leurs requêtes avec `"... WHERE name='" + name + "'"`. Permet dump de DB, contournement d'auth, suppression/modification de données.

#### S2 — Secret Flask hardcodé 🔴 Critique
- **Localisation :** l.14 `app.secret_key = "supersecret123"`
- **Description :** La clé secrète est dans le code source. Toute personne ayant accès au dépôt peut forger des sessions Flask arbitraires.

#### S3 — MD5 pour les mots de passe 🔴 Critique
- **Localisation :** `register()` l.70, `login()` l.86
- **Description :** MD5 est cassé depuis des décennies. Les mots de passe sont vulnérables aux rainbow tables. Doit être remplacé par bcrypt.

#### S4 — Routes admin sans aucune authentification 🔴 Critique
- **Localisation :** `list_users()` l.328–333, `reset_db()` l.336–344
- **Description :** `GET /admin/users` retourne tous les comptes. `POST /admin/reset` efface toute la base de données. Les deux sont accessibles sans aucune session.

#### S5 — Connexion DB globale avec `check_same_thread=False` 🔴 Critique
- **Localisation :** l.20 `conn = sqlite3.connect(DB_FILE, check_same_thread=False)`
- **Description :** SQLite n'est pas conçu pour le multi-thread partagé. Sous Flask en mode multi-worker, des requêtes concurrentes sur le même `conn` peuvent corrompre les données ou provoquer des deadlocks.

#### S6 — `GET /tasks/<id>/comments` sans authentification 🟠 Haut
- **Localisation :** `get_comments()` l.263–267
- **Description :** N'importe qui, sans session, peut lire tous les commentaires de toutes les tâches.

#### S7 — `export_data()` écrit un fichier sur le serveur 🟡 Moyen
- **Localisation :** `export_data()` l.360
- **Description :** Écrit `export_YYYY-MM-DD.json` à la racine du processus. Le nom est prédictible, pas de contrôle d'accès sur le fichier résultant.

---

### QUALITE

#### Q1 — `except:` nu (bare except) 🟠 Haut
- **Localisation :** `register()` l.77, `get_tasks()` l.182
- **Description :** Capture toutes les exceptions sans distinction. Masque les erreurs réelles (erreurs de syntaxe, KeyboardInterrupt, etc.). Le message d'erreur (`"already exists maybe"`) témoigne d'une incertitude sur le comportement.

#### Q2 — Aucune validation d'entrée 🟠 Haut
- **Localisation :** Tous les POST/PUT
- **Description :** `register()` accepte n'importe quel username/password. `create_task()` accepte `priority` et `project_id` non typés. `update_task()` insère directement dans la chaîne SQL. Pas de longueur max, pas de format de date vérifié.

#### Q3 — `print()` utilisé comme logging 🟡 Moyen
- **Localisation :** `init_db()` l.59, `create_task()` l.221
- **Description :** Les `print()` disparaissent en production selon la configuration du serveur. Doit être remplacé par `structlog` ou `logging`.

#### Q4 — Suppression en cascade sans transaction explicite 🟡 Moyen
- **Localisation :** `delete_project()` l.149–152, `delete_task()` l.254–257
- **Description :** Deux `DELETE` sans `BEGIN TRANSACTION`. Si le second échoue, les données sont dans un état incohérent.

#### Q5 — Import inutilisé 🟢 Faible
- **Localisation :** l.9 `import os`
- **Description :** `os` est importé mais jamais utilisé dans le fichier.

#### Q6 — `MAX_TASKS = 1000` déclaré mais jamais appliqué 🟢 Faible
- **Localisation :** l.17
- **Description :** Constante orpheline, commentaire "nobody will ever hit this" laisse supposer un contrôle qui n'existe pas.

---

### MAINTENABILITE

#### M1 — God module : tout dans `app.py` 🟠 Haut
- **Localisation :** Fichier entier (368 lignes)
- **Description :** Configuration Flask, init DB, ORM maison, logique métier, routes auth/projects/tasks/comments/admin/stats sont dans un seul fichier. Impossible à tester unitairement, impossible à faire évoluer indépendamment.

#### M2 — Accès aux colonnes par index numérique 🟠 Haut
- **Localisation :** Tous les handlers SELECT (`r[0]`, `r[1]`, `r[3]`…)
- **Description :** Si une colonne est ajoutée ou réordonnée, tous les accès silencieusement pointent sur la mauvaise valeur. Pas de modèle, pas de mapping.

#### M3 — Pas de suppression douce / pas de piste d'audit 🟡 Moyen
- **Localisation :** `delete_project()`, `delete_task()`
- **Description :** Les suppressions sont définitives et non traçables. En production, cela rend toute récupération impossible.

#### M4 — TODO/FIXME laissés en production 🟢 Faible
- **Localisation :** l.3, l.14, l.17, l.69, l.87, l.218, l.338
- **Description :** Commentaires de travail non résolus, dont `# TODO: add auth check` sur `reset_db()` — particulièrement dangereux.

---

## 4. Risques métier

| # | Risque | Sévérité | Route(s) |
|---|---|---|---|
| R1 | SQL injection sur `/login` → contournement auth complet + dump DB | 🔴 Critique | POST /login |
| R2 | `/admin/reset` sans auth → wiping de toute la base en prod | 🔴 Critique | POST /admin/reset |
| R3 | `/admin/users` sans auth → fuite de tous les comptes utilisateurs | 🔴 Critique | GET /admin/users |
| R4 | SQL injection sur `/tasks?status=` et `/search?q=` → exfiltration non loggée | 🔴 Critique | GET /tasks, GET /search |
| R5 | MD5 craqué → toute la table `users.password` est compromettable | 🔴 Critique | global |
| R6 | `secret_key` hardcodée → forge de session arbitraire (usurpation identité admin) | 🔴 Critique | global |
| R7 | Connexion DB partagée multi-thread → corruption silencieuse de données sous charge | 🔴 Critique | global |
| R8 | `delete_project` sans transaction → état incohérent (tasks orphelines si crash) | 🟠 Haut | DELETE /projects/\<id\> |
| R9 | `export_data()` écrit fichier prédictible sur disque → fuite de données | 🟡 Moyen | GET /export |

---

## 5. Points positifs

Ces comportements sont correctement implémentés et **doivent être préservés** lors du refacto :

1. **Vérification de session sur les routes utilisateur** — `if "user" not in session` est cohérent sur toutes les routes non-admin.
2. **Vérification du rôle admin pour DELETE /projects** — `session.get("role") != "admin"` est l'unique contrôle de rôle correct.
3. **Calcul des tâches en retard dans /stats** — comparaison de date textuelle `row[2] < today` fonctionne car le format ISO 8601 est lexicographiquement triable.
4. **Déduplication de projet** — `create_project()` vérifie l'existence par nom avant insertion.
5. **Tags JSON** — stockage de `tags` comme JSON sérialisé avec désérialisation à la lecture, pattern propre à conserver.
6. **Cascade comments → tasks** — `delete_task()` supprime d'abord les commentaires liés, évite les orphelins.
7. **Filtres cumulatifs sur GET /tasks** — logique `WHERE 1=1 AND ...` est le bon pattern, à réimplémenter avec des paramètres liés.

---

## Résumé exécutif

```
Smells total : 17
  Critiques  : 8  (SQL injection x4, secret, MD5, admin sans auth, conn globale)
  Hauts      : 5  (bare except, no validation, comments sans auth, god module, index col)
  Moyens     : 3  (print logging, pas de transaction, export fichier)
  Faibles    : 3  (import os, MAX_TASKS, TODO comments)

Risques métier : 9
  Critiques  : 7
  Hauts      : 1
  Moyens     : 1

Verdict : PRODUCTION NON RECOMMANDÉE en l'état.
          Les 8 smells critiques sont exploitables sans authentification préalable.
```
