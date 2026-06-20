# Standards qualité du projet Jacky

## Couverture de tests
- Minimum requis : **80% de couverture globale**
- Routes critiques (auth, admin) : **100%**
- Mesure : `pytest --cov=src --cov-report=term-missing`

## Complexité cyclomatique
- Limite par fonction : **10 max** (ruff / flake8-complexity)
- Fonctions > 30 lignes : refactoriser en sous-fonctions

## Type safety
- `mypy --strict` doit passer sans erreur
- Pas de `Any` sauf justification explicite en commentaire
- Paramètres optionnels typés avec `X | None` (Python 3.10+ syntax)

## Sécurité
### Mots de passe
```python
import bcrypt
def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())
```

### Secret key
```python
# config.py
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secret_key: str  # obligatoire — doit venir de l'env
    database_url: str = "sqlite:///data.db"
    debug: bool = False
    
    model_config = ConfigDict(env_file=".env")
```

### Validation des IDs dans les routes
```python
# Toujours convertir les path params en int
@bp.route("/<int:task_id>", methods=["GET"])
def get_task(task_id: int) -> Response:
    ...
```

## Revue de code (checklist avant chaque `/derive` commit)
- [ ] Pas de SQL brut
- [ ] Pas de bare except
- [ ] Type hints complets
- [ ] Tests ajoutés ou mis à jour
- [ ] Pas de secret hardcodé
- [ ] Logging structuré (pas de print)
- [ ] `mypy --strict` passe
- [ ] `ruff check` passe
- [ ] Couverture ≥ 80%

## Performance
- Pas de N+1 queries : utiliser `selectinload` / `joinedload` SQLAlchemy
- Pas de `.fetchall()` sur des tables sans limite : toujours paginer
- Indexer les colonnes filtrées fréquemment (status, project_id, assigned_to)

## Git
- Un commit par module refactorisé
- Format : `refactor(module): description courte`
- Branch : `refactor/<module>` → PR vers `main`
