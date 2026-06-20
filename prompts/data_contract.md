# Data Contracts — interfaces entre modules

> Ce fichier est mis à jour lors de `/draft` et enrichi pendant `/derive`.
> Il définit les contrats d'interface entre la couche routes, services, et modèles.

---

## Statut : NON DÉFINI

Ce fichier sera complété lors de la phase `/draft`.

Structure attendue :

```
## AuthService
### create_user(db, payload: UserCreateSchema) -> User
### authenticate(db, username, password) -> User | None

## TaskService
### list_tasks(db, filters: TaskFilterSchema) -> list[Task]
### create_task(db, payload: TaskCreateSchema) -> Task
### update_task(db, task_id: int, payload: TaskUpdateSchema) -> Task
### delete_task(db, task_id: int) -> None

## ProjectService
### list_projects(db) -> list[Project]
### create_project(db, payload: ProjectCreateSchema) -> Project
### delete_project(db, project_id: int) -> None

## Exceptions métier
### NotFoundError(AppError) — 404
### ForbiddenError(AppError) — 403
### DuplicateError(AppError) — 409
### ValidationError — levée par Pydantic
```

> À remplir par `/draft` avec les signatures complètes.
