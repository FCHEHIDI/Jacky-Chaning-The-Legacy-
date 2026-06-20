# /audit — Scoring technique par domaine

Argument optionnel : `/audit <fichier>` pour un audit ciblé.
Sans argument : audit global de `src/app.py`.

Lis `session/context.md`. Si un fichier est passé en argument, lis-le entièrement.

Produis un rapport de scoring selon ces 5 domaines :

## 1. Sécurité (OWASP Top 10)
Score : /10 — Vérifie :
- Injection SQL (A03)
- Authentification cassée (A07)
- Exposition de données sensibles (A02)
- Contrôle d'accès défaillant (A01)
- Mauvaise configuration de sécurité (A05)

## 2. Qualité du code
Score : /10 — Vérifie :
- Complexité cyclomatique
- Duplication
- Bare except
- Magic strings / numbers
- Dead code

## 3. Maintenabilité
Score : /10 — Vérifie :
- Séparation des responsabilités
- Type hints
- Docstrings
- Testabilité (dépendances injectables ?)
- Modularité

## 4. Robustesse
Score : /10 — Vérifie :
- Gestion des erreurs
- Validation des inputs
- Cas limites (division par zéro, null, vide)
- Race conditions potentielles

## 5. Conformité stack cible
Score : /10 — Vérifie :
- Distance par rapport à l'architecture cible définie dans `CLAUDE.md`
- Ce qui peut être migré directement vs ce qui nécessite une réécriture

**Score global = moyenne des 5 domaines**

Écris le rapport dans `logs/audit/audit_<date>.md` et crée un symlink (ou copie) `logs/audit/latest.md`.
Mets à jour `CLAUDE.md` — bloc "État courant".
Propose ensuite `/draft`.
