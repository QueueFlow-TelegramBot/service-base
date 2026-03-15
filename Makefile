.PHONY: help install install-dev compile-requirements run docker-up docker-down docker-build test test-cov clean logs

REQ_DIR=requirements

help:
	@echo "User Service - Available commands:"
	@echo "  make install      		- Create venv and install dependencies"
	@echo "  make install-dev  		- Install dev dependencies (includes test tools)"
	@echo "  make compile-requirements 	- Rebuild lock files with pip-tools"
	@echo "  make test         		- Run tests with pytest"
	@echo "  make test-cov     		- Run tests with coverage report"
	@echo "  make docker-up    		- Start services with Docker Compose"
	@echo "  make docker-down  		- Stop Docker Compose services"
	@echo "  make docker-build 		- Rebuild Docker images"
	@echo "  make logs         		- Show Docker logs"
	@echo "  make clean        		- Clean up Python cache and venv"

install:
	@echo "Creating virtual environment..."
	python3 -m venv venv
	@echo "Installing dependencies..."
	cd $(REQ_DIR) && ../venv/bin/pip install -r base.txt
	@echo "Done! Activate with: source venv/bin/activate"

install-dev:
	@echo "Creating virtual environment..."
	python3 -m venv venv
	@echo "Installing dev dependencies..."
	cd $(REQ_DIR) && ../venv/bin/pip install -r dev.txt
	@echo "Done! Activate with: source venv/bin/activate"

compile-requirements:
	@echo "Compiling requirement lock files..."
	./venv/bin/pip install pip-tools
	cd $(REQ_DIR) && ../venv/bin/pip-compile base.in --output-file base.txt
	cd $(REQ_DIR) && ../venv/bin/pip-compile dev.in --output-file dev.txt
	@echo "Requirements lock files updated."

docker-up:
	@echo "Starting services with Docker Compose..."
	docker-compose up -d
	@echo "Services started! API available at http://localhost:8000"
	@echo "Docs at http://localhost:8000/docs"

docker-down:
	@echo "Stopping Docker Compose services..."
	docker-compose down

docker-build:
	@echo "Building Docker images..."
	docker-compose build

logs:
	docker-compose logs -f

clean:
	@echo "Cleaning up..."
	rm -rf __pycache__ app/__pycache__ app/routers/__pycache__ tests/__pycache__
	rm -rf .pytest_cache htmlcov .coverage
	rm -rf venv
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleanup complete!"

test:
	@echo "Running tests..."
	./venv/bin/pytest

test-cov:
	@echo "Running tests with coverage..."
	./venv/bin/pytest --cov=app --cov-report=term-missing --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"
