# /compact — Compression du contexte session

Cette commande doit être exécutée :
- Automatiquement quand le contexte approche 70% d'utilisation
- Manuellement à la fin de chaque phase
- Sur demande explicite de l'utilisateur

## Procédure

### 1. Enregistrer un snapshot de métriques (slow feedback loop)
```bash
python scripts/state.py snapshot
```
Capture un point de données dans la série temporelle :
coverage_pct, tests_passing, mypy_errors, smells_open, modules_migrated.
C'est ce qui alimente le dashboard inter-sessions.

### 2. Exporter l'état depuis SQLite
```bash
# YAML compact pour injection contexte (< 300 tokens)
python scripts/state.py export yaml

# SQL dump pour versionnement git (commit ce fichier, pas state.db)
python scripts/state.py export sql
```
`session/context.yaml` = injection contexte prochaine session.
`session/state.sql` = mémoire longue versionnée, diff lisible sur GitHub.

### 2. Appender dans `session/history.md`
Ne jamais écraser ce fichier. Appendre :
```markdown
## Session <date ISO>
- Phase : <phase>
- Fichiers touchés : <liste>
- Décisions clés : <résumé>
- Métriques : <smells corrigés, tests ajoutés, modules migrés>
```

### 3. Mettre à jour next_action et active_file
Avant d'exporter, Claude DOIT écrire la prochaine action concrète :
```bash
python scripts/state.py set next_action "description précise de ce qui vient"
python scripts/state.py set active_file "src/routes/auth.py"  # fichier en cours
```
Sans `next_action` explicite, la prochaine session redémarre à l'aveugle.

### 4. Valider
```bash
python scripts/validate_compact.py
```
Vérifie que les 7 champs du "survival contract" sont présents.
Si `INVALID` — corriger avant de fermer la session.

### 5. Logger la compaction
```bash
python scripts/state.py log INFO "Context compacted" <phase_courante>
```

### 4. Mettre à jour `CLAUDE.md`
Met à jour le bloc "État courant" dans `CLAUDE.md` avec la phase courante.

### 5. Confirmer
Après écriture, réponds :
"✅ Contexte compacté. YAML à jour dans `session/context.yaml`. History appended."

## Note sur l'optimisation tokens
`session/context.yaml` est injecté à chaque session à la place du markdown verbose.
Structure : phase, decisions_recent (5 max), smells open/fixed, test metrics, risks.
Le YAML est généré depuis SQLite — la vérité reste dans la DB, pas dans le fichier.

### 2. Écrire le snapshot dans `session/context.md`
Ecrase le fichier avec ce format exact :

```markdown
# Context Snapshot — <date ISO>

## Phase courante
<phase active>

## Fichier actif
<chemin du fichier en cours de traitement>

## Décisions prises dans cette session
- <decision 1> — <justification courte>
- <decision 2> — <justification courte>

## Fichiers créés / modifiés
- <fichier> : <changement en 1 ligne>

## État des tests
- Total : X | Passants : Y | Échoués : Z

## TODO suivant
<prochaine action précise>

## Risques ouverts
- <risque 1>
```

### 3. Appendre dans `session/history.md`
Ne jamais écraser ce fichier. Appendre :

```markdown
## Session <date ISO>
- Phase : <phase>
- Fichiers touchés : <liste>
- Décisions clés : <résumé>
- Métriques : <lignes refactorisées, smells corrigés, tests ajoutés>
```

### 4. Mises à jour CLAUDE.md
Met à jour le bloc "État courant" dans `CLAUDE.md`.

### 5. Confirmer
Après écriture, réponds : "✅ Contexte compacté. Session sauvegardée dans `session/context.md`."
