# Refactor Logs — Project Jacky

> Un fichier par module refactorisé par `/derive`.
> Nommage : `<module>.md` (ex: auth.md, tasks.md)

## Format attendu pour chaque module
```markdown
# Refactor — <module>
Date : YYYY-MM-DD
Phase : /derive

## Smells corrigés
- SQL injection dans <fonction> → paramètres bindés SQLAlchemy
- ...

## Décisions prises
- [DECISION] Utilisation de Blueprint Flask pour isoler les routes

## Comportement préservé
- GET /tasks retourne toujours la même structure JSON
- ...

## Breaking changes
- Aucun / ou : <description>

## Tests ajoutés
- test_<module>.py : X nouveaux tests
```
