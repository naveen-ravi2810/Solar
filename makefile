server:
	uv run uvicorn main:app --reload --host 0.0.0.0

migrate:
	uv run alembic upgrade head

format:
	uv run ruff format .