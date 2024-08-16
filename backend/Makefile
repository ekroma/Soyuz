migrate:
	alembic revision --autogenerate
	alembic upgrade head
run:
	python3 main.py
downgrade:
	alembic downgrade -1