# Conventions de code — stack cible

## Python
- Version : 3.11+
- Formatter : `ruff format` (remplace Black)
- Linter : `ruff check` + `mypy --strict`
- Longueur de ligne : 100 caractères

## Nommage
| Élément | Convention | Exemple |
|---------|-----------|--------|
| Modules | snake_case | `auth_service.py` |
| Classes | PascalCase | `TaskService` |
| Fonctions | snake_case | `get_task_by_id` |
| Constantes | SCREAMING_SNAKE | `MAX_PASSWORD_LENGTH` |
| Enums | PascalCase + membres UPPER | `TaskStatus.IN_PROGRESS` |
| Variables privées | préfixe `_` | `_db_session` |

## Structure d'une fonction
```python
def create_task(db: Session, payload: TaskCreateSchema) -> Task:
    """Crée une tâche et la persiste.
    
    Raises:
        ProjectNotFoundError: si le projet n'existe pas
        ValidationError: si le payload est invalide (levée par Pydantic)
    """
    project = db.get(Project, payload.project_id)
    if not project:
        raise ProjectNotFoundError(payload.project_id)
    task = Task(**payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
```

## Imports
Ordre strict (ruff isort) :
1. stdlib
2. third-party
3. local (relatifs avec `.`)

## Flask Blueprints
```python
from flask import Blueprint
bp = Blueprint("tasks", __name__, url_prefix="/tasks")
```

## SQLAlchemy
- Sessions injectées via dépendance (pas de global)
- `db.session` passé en paramètre aux services
- Modèles dans `src/models/`, un fichier par modèle
- Migrations avec Alembic

## Pydantic
- Schémas de validation dans `src/schemas/`
- `BaseModel` pour les inputs/outputs
- `model_config = ConfigDict(from_attributes=True)` pour les réponses ORM

## Gestion d'erreurs
```python
# Exceptions métier dans src/exceptions.py
class AppError(Exception):
    status_code: int = 500
    message: str = "Internal server error"

class NotFoundError(AppError):
    status_code = 404

class ForbiddenError(AppError):
    status_code = 403
```

## Logging structlog
```python
import structlog
log = structlog.get_logger(__name__)
log.info("task_created", task_id=task.id, user=current_user)
```
