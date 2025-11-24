.PHONY: help install test run clean docker-build docker-run lint format

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make test         - Run tests"
	@echo "  make test-cov     - Run tests with coverage"
	@echo "  make run          - Run development server"
	@echo "  make run-prod     - Run production server with gunicorn"
	@echo "  make lint         - Run linting checks"
	@echo "  make format       - Format code"
	@echo "  make clean        - Clean temporary files"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run   - Run with Docker Compose"

install:
	pip install -r requirements.txt

test:
	pytest -v

test-cov:
	pytest --cov=app --cov-report=html --cov-report=term

run:
	python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-prod:
	gunicorn app.main:app -c gunicorn.conf.py

lint:
	@echo "Running flake8..."
	-flake8 app/ tests/
	@echo "Running mypy..."
	-mypy app/

format:
	@echo "Formatting with black..."
	black app/ tests/
	@echo "Sorting imports with isort..."
	isort app/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf htmlcov/
	rm -rf .coverage

docker-build:
	docker build -t pii-extraction-service .

docker-run:
	docker-compose up

docker-stop:
	docker-compose down

setup-env:
	cp .env.example .env
	@echo "Created .env file. Please edit it with your API keys."
