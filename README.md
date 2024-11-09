# users-api
the name is api, users api


### API
When creating the api I opted to first create a base router, `UsersRouter`, and then each new feature/business function would subclass a router from there. Then each router is attached to the `root_router`. This allows for the following things to be true:
- Easily label and version routes based on prefixes
- Allows different routers to have the same sub-endpoint names. ex. `/users` -> `/v1/users`
- Enforce tokens at the `root_router` level

### DB
The `db` is mostly all boilerplate I've collected over the years. It provides the following:
- A scalable generator for injecting the data base session to each request
- common types for default table columns `id`, `created_at`, `last_updated`, etc.
- environment variables for alembic during migrations
- I've explored adding AsyncSession support, but haven't had a need for it yet

### Domains
All logic that doesn't belong directly in the endpoint, but also doesn't directly touch the database. Typically is where I implement objects defined in `/services`.

This is currently empty.

### Managers
Where we interface with the database. Each table gets a "Manager". `User` -> `UserManager`. A manager abstracts all the functional database code away from the immediate request path. Managers are imported as singletons to increase performance (especially for database pooling at scale). 

### Models
Houses both standard pydantic models and ORM models. I've never liked this design because you often end up defining a model like `User` twice: once in the orm, and again in root of `/models`. It works, but gets cumbersome at scale. I've been looking into `sqlmodel` lately.

### Schemas
Houses all pydantic models used in request/response flows for endpoints.

### Services
For storing all code/logic for third-party or internal microservices. 

This is currently empty.

## Project Structure
```
├── /users_api
│ ├── app.py
│ ├── app_factory.py
│ ├── enums.py
│ ├── helper.py
│ ├── settings.py
│ ├── api/
│ ├── db/
│ ├── domains/
│ ├── managers/
│ ├── models/
│ ├── schemas/
│ ├── services/
└── /
```

## Run locally

Setup `.env` file
```sh
cp .env.example .env
```

Install dependencies
```sh
poetry install
```

Run server locally
```sh
make server
```
*Note: Runs this command `poetry run uvicorn --reload users_api.app:app --host 0.0.0.0 --port 9898`*

## Database Migrations

Create migration
```sh
make alembic-migration
```

Upgrade DB

*Runs all migrations*
```sh
make db-up
```

Downgrade DB

*Only reverts the previous migration, run over and over to keep reverting older migrations*
```
make db-down
```

## Testing
Run test suite
```
make tests
```
*Runs this command `poetry run pytest tests/`*

## Docker

Build
```sh
docker build -t auth .
```

Run
```sh
docker run users_api
```

Should look something like
```
INFO:     Will watch for changes in these directories: ['/Users/sammccaffrey/Projects/users-api']
INFO:     Uvicorn running on http://0.0.0.0:3000 (Press CTRL+C to quit)
INFO:     Started reloader process [77993] using StatReload
Running on Python 3.10.13. The recommended Python is ~3.10.3.
INFO:     Started server process [77997]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
``` 