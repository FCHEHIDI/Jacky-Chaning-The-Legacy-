# /map — Carte des dépendances et zones de risque

Lis `session/context.md` et `logs/audit/survey.md`.

Génère une carte structurée du code en 4 sections :

## 1. Graphe de dépendances
Pour chaque module/fonction, liste :
- Ce qu'il appelle (dépendances sortantes)
- Ce qui l'appelle (dépendances entrantes)
- Couplage estimé : fort / moyen / faible

## 2. Zones de risque identifiées
Class chaque zone par niveau de risque et explique pourquoi :
- 🔴 Zone rouge : ne pas modifier sans tests couvrant 100% des cas
- 🟠 Zone orange : modifier avec précaution, tests requis
- 🟢 Zone verte : peut être refactorisée librement

## 3. Clusters fonctionnels
Regroupe les fonctions par domaine métier (auth, projects, tasks, admin, analytics).
Pour chaque cluster : périmètre, dépendances inter-cluster, candidat à isoler en Blueprint.

## 4. Ordre de refacto recommandé
Propose un ordre d'intervention (du moins risqué au plus risqué) avec justification.

Écris le rapport dans `logs/audit/map.md`.
Mets à jour `CLAUDE.md` — bloc "État courant".
Propose ensuite `/audit`.
