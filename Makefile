HERE := $(shell basename $(CURDIR))
PROJECT := "rock_me"
PYTHON := "python3.6"
VENV_DIR := "$(HOME)/venvs"
DEP_FILE := "scripts/os-deps.apt"

test:
	@py.test

run:
	@( \
		. $(VENV_DIR)/$(PROJECT)/bin/activate; \
		python manage.py runserver; \
	)

run8000:
	@( \
		. $(VENV_DIR)/$(PROJECT)/bin/activate; \
		python manage.py runserver 0.0.0.0:8000; \
	)

migrations:
	@( \
		. $(VENV_DIR)/$(PROJECT)/bin/activate; \
		python manage.py makemigrations; \
	)

migrate:
	@( \
		. $(VENV_DIR)/$(PROJECT)/bin/activate; \
		python manage.py migrate; \
	)

sass:
	@( \
		. $(VENV_DIR)/$(PROJECT)/bin/activate; \
		python scripts/compile-sass.py $(PROJECT); \
	)

shell:
	@( \
		. ~/venvs/$(PROJECT)/bin/activate; \
		python manage.py shell; \
	)

os_install:
	# Bootstrap the current environment for running DeCart
	@./scripts/bootstrap-ubuntu.sh $(DEP_FILE)

install:
	@( \
		$(PYTHON) -m pip install virtualenv; \
		[ -d $(VENV_DIR) ] || mkdir $(VENV_DIR); \
		$(PYTHON) -m virtualenv $(VENV_DIR)/$(PROJECT); \
		. $(VENV_DIR)/$(PROJECT)/bin/activate; \
		pip install -r scripts/py-dev.txt; \
	)

newapp:
	@( \
		. $(VENV_DIR)/$(PROJECT)/bin/activate; \
		python manage.py startapp $(NAME); \
	)

project:
	@. $(VENV_DIR)/$(PROJECT)/bin/activate
	@python manage.py startproject $(NAME)

superuser:
	@( \
		. $(VENV_DIR)/$(PROJECT)/bin/activate; \
		python manage.py createsuperuser; \
	)

stats:
	@cloc .

db_visual:
	@( \
		. $(VENV_DIR)/$(PROJECT)/bin/activate; \
		./scripts/visualise-db.sh; \
	)

# NOTE: Add other fixture files here when they are written
seed_db:
	@( \
		. $(VENV_DIR)/$(PROJECT)/bin/activate; \
		python manage.py loaddata rock_me/fixtures/city.json; \
		python manage.py loaddata decart/core/fixtures/kpi_category.json; \
		python manage.py loaddata decart/core/fixtures/kpi.json; \
	)

# Delete all migration .py and .pyc files then reset the DB
reset_db:
	@( \
		. $(VENV_DIR)/$(PROJECT)/bin/activate; \
		./scripts/with-env flush; \
		find . -type f -wholename '*migrations/[^_]*.py' -delete; \
		find . -type f -wholename '*migrations/__pycache__/*' -delete; \
		find . -type d -wholename '*migrations/__pycache__' -delete; \
		find $(VENV_DIR) -type f -wholename '*decart/core/migrations/[^_]*.py' -delete; \
		find $(VENV_DIR) -type f -wholename '*decart/core/migrations/__pycache__/*' -delete; \
		find $(VENV_DIR) -type d -wholename '*decart/core/migrations/__pycache__' -delete; \
		make migrations; \
		make migrate; \
		make superuser; \
		make seed_db; \
		python manage.py shell < scripts/import_users.py; \
	)

clear_migrations:
	@( \
		echo "Clearing existing migration files..."; \
		find . -type f -wholename '*migrations/[^_]*.py' -delete; \
		find . -type f -wholename '*migrations/__pycache__/*' -delete; \
		find . -type d -wholename '*migrations/__pycache__' -delete; \
		find $(VENV_DIR) -type f -wholename '*decart/core/migrations/[^_]*.py' -delete; \
		find $(VENV_DIR) -type f -wholename '*decart/core/migrations/__pycache__/*' -delete; \
		find $(VENV_DIR) -type d -wholename '*decart/core/migrations/__pycache__' -delete; \
		echo "Done."; \
	)

init_rock:
	@( \
		. $(VENV_DIR)/$(PROJECT)/bin/activate; \
		make migrations; \
		make migrate; \
		make superuser; \
		make seed_db; \
		python manage.py shell < scripts/import_users.py; \
	)
