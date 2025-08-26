.PHONY: help install-deps run-api run-pipeline

# Helper commands
help:
	@echo "Available commands:"
	@echo "  install-deps       : Install Python dependencies from requirements.txt"
	@echo "  run-api            : Start the FastAPI server"
	@echo "  run-pipeline       : Run the ML training/prediction pipeline"

# Install Python dependencies from requirements.txt
install-deps:
	@echo "Installing dependencies..."
	pip install -r .devcontainer/requirements.txt --break-system-packages

# Run the uvicorn server
run-api:
	@echo "Starting the server..."
	python -m app.main

# Run the model pipeline
run-pipeline:
	@echo "Running the model pipeline"
	python -m app.models.ml_models.src.pipeline