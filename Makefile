service_name = users_api

.PHONY: server
server:
	poetry run uvicorn --reload users_api.app:app --host 0.0.0.0 --port 3000

MERGE_BASE = $(shell git merge-base HEAD main)

# Pre-commit against branch changes
.PHONY: lint-branch
lint-branch:
	poetry run pre-commit run --from-ref $(MERGE_BASE) --to-ref HEAD

#####################
# Database Commands #
#####################

# Creates a `audienceplus` superuser to work with the DB. This is unlike our production
# environments which have per-service and per-user roles to isolate DB permissions.
.PHONY: create-db-users
create-db-users:
	psql postgres -tc "SELECT 1 FROM pg_roles where rolname = 'audienceplus'" | grep -q 1 || psql postgres -c "CREATE ROLE audienceplus WITH SUPERUSER LOGIN CREATEDB CREATEROLE"

# Creates ${service_name} databases along with the necessary schemas
# see wind/databases/${service_name} for details about which schemas should exist
.PHONY: create-db
create-db:
	psql postgres -tc "SELECT 1 FROM pg_database WHERE datname = '${service_name}'" | grep -q 1 || psql postgres -c "CREATE DATABASE ${service_name} OWNER audienceplus"
	psql postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'test_${service_name}'" | grep -q 1 || psql postgres -c "CREATE DATABASE test_${service_name} OWNER audienceplus"

# Drops databases created by create-db
.PHONY: drop-db
drop-db:
	psql postgres -c "DROP DATABASE ${service_name}"
	psql postgres -c "DROP DATABASE test_${service_name}"

# Drops users created by create-db-user
.PHONY: drop-db-users
drop-db-users:
	psql postgres -c "DROP USER IF EXISTS audienceplus"

# Adds necessary database extensions
# NOTE: The pg-cron extension will throw errors for most developers (until PP-5185 is
#       completed). If you see these errors, feel free to delete the pg-cron lines
#       locally. As long as SHOULD_SCHEDULE_HARD_DELETE_WITH_PGCRON=false is in your
#       .env file there will be no issues.
# .PHONY: add-db-extensions
# add-db-extensions:
# 	psql ${service_name} -c 'CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; CREATE EXTENSION IF NOT EXISTS "pg_trgm";'
# 	# Disable local activation of pg-cron until we have a good dev experience for
# 	# installing the required extension binaries/etc.
# 	# psql ${service_name} -c 'CREATE EXTENSION IF NOT EXISTS "pg-cron";'

# 	psql test_${service_name} -c 'CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; CREATE EXTENSION IF NOT EXISTS "pg_trgm";'

# Upgrades local db with any new migrations
.PHONY: upgrade-db
upgrade-db:
	poetry run alembic upgrade head

# Upgrades local test db with any new migrations
.PHONY: upgrade-test-db
upgrade-test-db:
	ENV=test poetry run alembic upgrade head

# Adds db users, creates db, installs extensions, and runs all migrations
.PHONY: db
db: create-db-users create-db upgrade-db

# Reset db
.PHONY: reset-db
reset-db:
	make drop-db
	make db

# Create a new alembic version
.PHONY: alembic-migration
alembic-migration:
	@echo "Migration Description: "; \
    read MIGRATION_DESC; \
	PYTHONPATH=. poetry run alembic revision --autogenerate -m "$$MIGRATION_DESC"

# Undo last alembic migration
.PHONY: undo-alembic-migration
undo-alembic-migration:
	poetry run alembic downgrade -1
