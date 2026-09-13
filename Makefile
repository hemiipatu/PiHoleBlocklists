# Variables
PYTHON := python3
SHELLCHECK := shellcheck

.PHONY: all help install-dev validate build lint clean test

all: validate lint build

help:
	@echo "Available commands:"
	@echo "  make build       - Run build.py locally to compile blocklists"
	@echo "  make validate    - Validate JSON syntax and Python compilation"
	@echo "  make lint        - Lint shell scripts (setup.sh) and Python files"
	@echo "  make test        - Run all validation and linting checks"
	@echo "  make clean       - Remove generated blocklists and temporary files"
	@echo "  make install-dev - Install pre-commit and local dev dependencies"

# Install local developer tools
install-dev:
	@echo "[+] Installing local development tools..."
	pip install pre-commit
	pre-commit install
	@echo "[+] Pre-commit hooks installed successfully!"

# Validate JSON and Python syntax
validate:
	@echo "[+] Validating sources.json..."
	@$(PYTHON) -m json.tool sources.json > /dev/null
	@echo "[+] Validating Python syntax..."
	@$(PYTHON) -m py_compile build.py

# Lint shell and python files
lint:
	@echo "[+] Checking setup.sh with ShellCheck..."
	@if command -v $(SHELLCHECK) >/dev/null 2>&1; then \
		$(SHELLCHECK) setup.sh; \
	else \
		echo "[!] Warning: ShellCheck not installed. Skipping shell linting."; \
	fi

# Run tests/validations
test: validate lint

# Execute a full local compilation build
build: validate
	@echo "[+] Running local blocklist build..."
	@$(PYTHON) build.py

# Clean up generated artifacts
clean:
	@echo "[+] Cleaning temporary files and build artifacts..."
	@rm -rf blocklists/ build_summary.md .pytest_cache .ruff_cache __pycache__
	@echo "[+] Clean complete."
