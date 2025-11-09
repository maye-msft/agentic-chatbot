lint-all:
	poetry run black .
	poetry run ruff check --fix .
	poetry run mypy .
	poetry run pydoclint .
	poetry run pymarkdown scan .
	poetry run yamllint . -c .yamllint.yaml

check-all:
	poetry run black . --check
	poetry run ruff check .
	poetry run mypy .
	poetry run pydoclint .
	poetry run pymarkdown scan .
	poetry run yamllint . -c .yamllint.yaml

test-all:
	poetry run pytest .

# Subproject-specific targets will be added by create_python_subproject.sh

test-core:
	poetry run pytest core/tests

test-core-coverage:
	poetry run pytest --disable-warnings --maxfail=1 --cov=core core/tests
