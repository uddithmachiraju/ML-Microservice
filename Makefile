.PHONY: install-dependencies clean

# Helper commands
help:
	@echo "Available commands..."
	@echo "install-dependencies : Installs the dependencies from the requirements file"

# Install Python dependencies from requirements.txt
install-dependencies:
	@echo "Installing dependencies..."
	pip install -r .devcontainer/requirements.txt --break-system-packages

# Run the uvicorn server
run-api:
	@echo "Starting the server..."
	python -m app.main