.PHONY: all build clean test validate

all: validate build

# Run syntax and configuration checks
validate:
	@echo "Checking sources.json syntax..."
	@python3 -m json.tool sources.json > /dev/null
	@echo "Validating Python code..."
	@python3 -m py_compile build.py

# Run a local build test
build:
	@echo "Running local blocklist build..."
	@python3 build.py

# Lint shell scripts locally (requires shellcheck installed)
test:
	@shellcheck setup.sh

# Clean generated artifacts
clean:
	@rm -rf blocklists/ build_summary.md setup.sh.tmp
	@echo "Cleaned build artifacts."
