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


test-stock_price_agent:
	poetry run pytest stock_price_agent/tests

test-stock_price_agent-coverage:
	poetry run pytest --disable-warnings --maxfail=1 --cov=stock_price_agent stock_price_agent/tests


test-test_simple_agent:
	poetry run pytest test_simple_agent/tests

test-test_simple_agent-coverage:
	poetry run pytest --disable-warnings --maxfail=1 --cov=test_simple_agent test_simple_agent/tests


test-test_empty_tools:
	poetry run pytest test_empty_tools/tests

test-test_empty_tools-coverage:
	poetry run pytest --disable-warnings --maxfail=1 --cov=test_empty_tools test_empty_tools/tests


test-stock_agent:
	poetry run pytest stock_agent/tests

test-stock_agent-coverage:
	poetry run pytest --disable-warnings --maxfail=1 --cov=stock_agent stock_agent/tests


test-test_prompt_file:
	poetry run pytest test_prompt_file/tests

test-test_prompt_file-coverage:
	poetry run pytest --disable-warnings --maxfail=1 --cov=test_prompt_file test_prompt_file/tests
