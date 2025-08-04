# Makefile for JSON to HTML conversion
# Usage: make [target]

# Default variables
INPUT_FILE = contents.json
OUTPUT_DIR = output
SCRIPT = json_to_html.py

# Default target
.PHONY: all
all: html

# Help target
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  help         - Show this help message"
	@echo "  html         - Convert all articles to HTML (default)"
	@echo "  recent       - Convert recent 10 articles to HTML"
	@echo "  latest       - Convert latest 5 articles to HTML"
	@echo "  clean        - Remove generated HTML files"
	@echo "  test         - Test the conversion script"
	@echo ""
	@echo "Variables:"
	@echo "  INPUT_FILE   - Input JSON file (default: contents.json)"
	@echo "  OUTPUT_DIR   - Output directory (default: output)"
	@echo "  SIZE         - Number of articles to include"
	@echo ""
	@echo "Examples:"
	@echo "  make html"
	@echo "  make recent"
	@echo "  make latest"
	@echo "  make html INPUT_FILE=data.json"
	@echo "  make recent SIZE=7"

# Create output directory
$(OUTPUT_DIR):
	mkdir -p $(OUTPUT_DIR)

# Convert all articles to HTML
.PHONY: html
html: $(OUTPUT_DIR)
	uv run python $(SCRIPT) --input $(INPUT_FILE) --output $(OUTPUT_DIR)/articles.html
	@echo "✅ All articles converted to $(OUTPUT_DIR)/articles.html"

# Convert recent articles (default 10)
.PHONY: recent
recent: $(OUTPUT_DIR)
	uv run python $(SCRIPT) --input $(INPUT_FILE) --output $(OUTPUT_DIR)/articles.html --size $(or $(SIZE),10)
	@echo "✅ Recent $(or $(SIZE),10) articles converted to $(OUTPUT_DIR)/articles.html"

# Convert latest articles (default 5)
.PHONY: latest
latest: $(OUTPUT_DIR)
	uv run python $(SCRIPT) --input $(INPUT_FILE) --output $(OUTPUT_DIR)/articles.html --size $(or $(SIZE),5)
	@echo "✅ Latest $(or $(SIZE),5) articles converted to $(OUTPUT_DIR)/articles.html"

# Custom size conversion
.PHONY: custom
custom: $(OUTPUT_DIR)
ifndef SIZE
	@echo "❌ Error: SIZE variable is required for custom target"
	@echo "Usage: make custom SIZE=10"
	@exit 1
endif
	uv run python $(SCRIPT) --input $(INPUT_FILE) --output $(OUTPUT_DIR)/articles_$(SIZE).html --size $(SIZE)
	@echo "✅ $(SIZE) articles converted to $(OUTPUT_DIR)/articles_$(SIZE).html"

# Test the script
.PHONY: test
test:
	@echo "🧪 Testing JSON to HTML conversion script..."
	uv run python $(SCRIPT) --help
	@echo ""
	@echo "✅ Script is working correctly"

# Validate input JSON file
.PHONY: validate
validate:
	@echo "🔍 Validating JSON file: $(INPUT_FILE)"
	uv run python -c "import json; data=json.load(open('$(INPUT_FILE)')); print(f'✅ Valid JSON with {len(data)} articles')"

# Clean generated files
.PHONY: clean
clean:
	rm -rf $(OUTPUT_DIR)
	rm -f *.html
	@echo "🧹 Cleaned up generated HTML files"

# Open the generated HTML in browser (if available)
.PHONY: open
open: html
	@if command -v xdg-open >/dev/null 2>&1; then \
		xdg-open $(OUTPUT_DIR)/all_articles.html; \
		echo "🌐 Opened HTML file in browser"; \
	elif command -v open >/dev/null 2>&1; then \
		open $(OUTPUT_DIR)/all_articles.html; \
		echo "🌐 Opened HTML file in browser"; \
	else \
		echo "ℹ️  Generated file: $(OUTPUT_DIR)/all_articles.html"; \
	fi

# Show file information
.PHONY: info
info:
	@echo "📊 File Information:"
	@echo "Input file: $(INPUT_FILE)"
	@if [ -f "$(INPUT_FILE)" ]; then \
		echo "  - Size: $$(du -h $(INPUT_FILE) | cut -f1)"; \
		echo "  - Articles: $$(uv run python -c "import json; print(len(json.load(open('$(INPUT_FILE)'))))" 2>/dev/null || echo "Unknown")"; \
	else \
		echo "  - ❌ File not found"; \
	fi
	@echo "Output directory: $(OUTPUT_DIR)"
	@if [ -d "$(OUTPUT_DIR)" ]; then \
		echo "  - HTML files: $$(ls $(OUTPUT_DIR)/*.html 2>/dev/null | wc -l)"; \
	else \
		echo "  - Directory not created yet"; \
	fi

# Development targets
.PHONY: dev
dev: validate test html
	@echo "🚀 Development build complete"

# Production build with all sizes
.PHONY: build
build: clean $(OUTPUT_DIR)
	@echo "🏗️  Building all HTML versions..."
	make html
	make recent SIZE=5
	make latest SIZE=3
	make custom SIZE=10
	@echo "✅ Production build complete"
	@echo "Generated files:"
	@ls -la $(OUTPUT_DIR)/*.html

# Watch for changes (requires inotify-tools)
.PHONY: watch
watch:
	@echo "👀 Watching for changes in $(INPUT_FILE)..."
	@if command -v inotifywait >/dev/null 2>&1; then \
		while inotifywait -e modify $(INPUT_FILE); do \
			echo "🔄 File changed, regenerating HTML..."; \
			make html; \
		done; \
	else \
		echo "❌ inotifywait not found. Install inotify-tools to use watch feature."; \
		echo "On Ubuntu/Debian: sudo apt-get install inotify-tools"; \
	fi

# Show current directory structure
.PHONY: tree
tree:
	@echo "📁 Directory structure:"
	@if command -v tree >/dev/null 2>&1; then \
		tree -I '__pycache__|*.pyc' .; \
	else \
		find . -type f -name "*.json" -o -name "*.html" -o -name "*.py" -o -name "Makefile" | sort; \
	fi

# Run gemini CLI with prompt file
.PHONY: prompt
prompt:
	@echo "🚀 Running Gemini CLI with contents.prompt..."
	make -f gemini-cli-prompt.mk FILE="contents.prompt"
	@echo "✅ Gemini CLI execution completed"

# Test Gemini API connectivity and quota
.PHONY: test-api
test-api:
	@echo "🔍 Testing Gemini API status..."
	make -f gemini-cli-prompt.mk test-api
