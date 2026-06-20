# /doctor — Diagnostic de blockers et régressions

Commande transversale utilisable à tout moment.
Utilise-la quand : des tests échouent de façon inexpliquée, une dépendance bloque, une décision semble contradictoire, ou le contexte semble incohérent.

## Procédure de diagnostic

### 1. Lire le contexte
Lis `session/context.md` et `CLAUDE.md` — bloc "État courant".

### 2. Identifier le symptôme
Décris précisément le problème observé :
- Message d'erreur exact (si applicable)
- Comportement attendu vs comportement observé
- Dernière action effectuée avant l'apparition du problème

### 3. Analyser les causes probables
Propose une liste ordonnée de causes (la plus probable en premier) avec :
- Probabilité estimée
- Preuve ou indice qui pointe vers cette cause
- Impact si confirmée

### 4. Plan de résolution
Pour chaque cause identifiée, propose :
- Action corrective minimale
- Commande à lancer pour vérifier
- Rollback possible si l'action aggrave le problème

### 5. Vérification post-fix
- Liste les tests à relancer pour confirmer la résolution
- Décrit l'état attendu après correction

### 6. Logger la résolution
Ecris dans `logs/sessions/<session-en-cours>.md` :
```
[WARN] <date> — Blocker détecté : <description>
[DECISION] <date> — Fix appliqué : <description>
[DONE] <date> — Résolu. Tests : OK
```

### 7. Mettre à jour le contexte
Si la résolution change l'état du projet, lance `/compact` après.
