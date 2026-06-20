# /survey — Inventaire brut du legacy

## Initialisation
Avant de lire le code, exécute dans le terminal :
```bash
python scripts/state.py phase set survey in_progress
```

Lis `session/context.yaml` (compact, machine-readable), puis `src/app.py` en entier.

Produis un rapport exhaustif structuré ainsi :

## 1. Métriques brutes
- Nombre de lignes, de routes, de fonctions
- Imports utilisés
- Tables et relations DB
- Dépendances externes

## 2. Inventaire des routes
Pour chaque route : méthode HTTP, chemin, auth requise, opérations DB, valeurs retournées.

## 3. Catalogue des smells
Pour chaque smell trouvé, **execute immédiatement** :
```bash
python scripts/state.py smell add "<nom>" "<localisation>" <critical|high|medium|low>
```
Categorie (sécurité / qualité / maintenabilité), description courte.

## 4. Risques métier
Liste des opérations qui pourraient avoir un impact en production si cassées.
Pour chaque risque :
```bash
python scripts/state.py log RISK "<description>" survey
```

## 5. Points positifs
Ce qui fonctionne et doit être préservé (comportement observable).

## Finalisation
Ecris le rapport dans `logs/audit/survey.md`.

Vérifie la gate :
```bash
python scripts/check_gate.py survey
```
Si la gate est ouverte :
```bash
python scripts/state.py phase set survey completed
```
Mets à jour `CLAUDE.md` — bloc "État courant".
Propose ensuite `/map`.

Produis un rapport exhaustif structuré ainsi :

## 1. Métriques brutes
- Nombre de lignes, de routes, de fonctions
- Imports utilisés
- Tables et relations DB
- Dépendances externes

## 2. Inventaire des routes
Pour chaque route : méthode HTTP, chemin, auth requise, opérations DB, valeurs retournées.

## 3. Catalogue des smells
Pour chaque smell trouvé :
- Catégorie (sécurité / qualité / maintenabilité)
- Localisation exacte (nom de fonction, ligne approximative)
- Sévérité : 🔴 Critique / 🟠 Haut / 🟡 Moyen / 🟢 Faible
- Description courte

## 4. Risques métier
Liste des opérations qui pourraient avoir un impact en production si cassées.

## 5. Points positifs
Ce qui fonctionne et doit être préservé (comportement observable).

À la fin, mets à jour `CLAUDE.md` — bloc "État courant" — avec :
```
PHASE ACTIVE : MAP
DERNIÈRE DÉCISION : survey terminé
```

Ecris le rapport dans `logs/audit/survey.md`.
Propose ensuite `/map`.
