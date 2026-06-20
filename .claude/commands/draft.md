# /draft — Plan d'intervention et contrats d'interface

Lis dans cet ordre :
1. `session/context.md`
2. `logs/audit/latest.md`
3. `prompts/conventions.md`
4. `prompts/data_contract.md`

Produis le plan de refacto en 4 parties :

## 1. Ordre d'intervention
Liste ordonnée des modules à créer/migrer.
Pour chaque module :
- Nom de fichier cible
- Responsabilité unique
- Dépendances (ce dont il a besoin)
- Risque d'intervention : faible / moyen / haut

## 2. Contrats d'interface
Pour chaque service/module cible, définis :
- La signature des fonctions publiques (types Python)
- Les exceptions qu'elles peuvent lever
- Ce qu'elles ne font PAS (hors périmètre)

## 3. Stratégie de migration DB
- Passage de `sqlite3` brut vers SQLAlchemy ORM
- Ordre de migration des tables
- Gestion de la rétrocompatibilité des données

## 4. Critères d'acceptation par module
Pour chaque module, définis les tests minimaux qui valideront la migration.

Écris le plan dans `logs/audit/draft.md`.
Mets à jour `prompts/data_contract.md` avec les contrats définis.
Mets à jour `CLAUDE.md` — bloc "État courant".
Propose ensuite `/stabilize`.
