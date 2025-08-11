USER_ID := $(shell id -u)
GROUP_ID := $(shell id -g)
# change user and passwd if you use it

# Default prompt if none provided
PROMPT ?= 
FILE ?=

# Set default target
.DEFAULT_GOAL := all

all:
	@echo "Checking if gemini-app image exists..."
	@if ! docker image inspect gemini-app >/dev/null 2>&1; then \
		echo "gemini-app image not found. Building..."; \
		docker build --build-arg USER_ID=$(USER_ID) --build-arg GROUP_ID=$(GROUP_ID) -t gemini-app .; \
	else \
		echo "gemini-app image found, proceeding..."; \
	fi
	@echo "Executing Gemini CLI with FILE=$(FILE)..."
	@echo "FILE variable content: '$(FILE)'"
	@echo "Current date: $$(date '+%Y-%m-%d (%A)')"
	@if [ -n "$(FILE)" ]; then \
		echo "FILE is set, reading from file: $(FILE)"; \
		if [ -f "$(FILE)" ]; then \
			echo "File exists, reading content and executing directly..."; \
			CURRENT_DATE="$$(date '+%Y-%m-%d (%A)')"; \
			echo "Adding current date: $$CURRENT_DATE"; \
			FILE_CONTENT="Current date: $$CURRENT_DATE\n\n$$(cat "$(FILE)")"; \
			echo "Command: docker run -it --rm -v ./:/usr/src/app -e GEMINI_API_KEY=*** gemini-app gemini chat -y -p \"[FILE_CONTENT]\""; \
			if docker run -it --rm -v ./:/usr/src/app -e GEMINI_API_KEY=AIzaSyB647F_VzNA0tT8kacPMLTbL62EWEChmyw gemini-app gemini chat -y -p "$$FILE_CONTENT"; then \
				echo "✅ Gemini CLI executed successfully"; \
			else \
				echo "❌ Gemini CLI failed with exit code: $$?"; \
				echo "Possible causes:"; \
				echo "  - API quota exceeded"; \
				echo "  - Network connectivity issues"; \
				echo "  - Invalid API key"; \
				echo "  - Service temporarily unavailable"; \
			fi; \
		else \
			echo "Error: File $(FILE) not found!"; \
		fi; \
	else \
		echo "FILE is not set, using PROMPT variable..."; \
		echo "Command: docker run -it --rm -v ./:/usr/src/app -e GEMINI_API_KEY=*** gemini-app gemini chat -y"; \
		CURRENT_DATE="$$(date '+%Y-%m-%d (%A)')"; \
		PROMPT_WITH_DATE="Current date: $$CURRENT_DATE\n\n$(PROMPT)"; \
		if echo "$$PROMPT_WITH_DATE" | docker run -i --rm -v ./:/usr/src/app -e GEMINI_API_KEY=AIzaSyB647F_VzNA0tT8kacPMLTbL62EWEChmyw gemini-app gemini chat -y --prompt "$PROMPT"; then \
			echo "✅ Gemini CLI executed successfully"; \
		else \
			echo "❌ Gemini CLI failed with exit code: $$?"; \
			echo "Possible causes:"; \
			echo "  - API quota exceeded"; \
			echo "  - Network connectivity issues"; \
			echo "  - Invalid API key"; \
			echo "  - Service temporarily unavailable"; \
		fi; \
	fi

# Check if gemini-app image exists, build if not
check-image:
	@if ! docker image inspect gemini-app >/dev/null 2>&1; then \
		echo "gemini-app image not found. Building..."; \
		docker build --build-arg USER_ID=$(USER_ID) --build-arg GROUP_ID=$(GROUP_ID) -t gemini-app .; \
	else \
		echo "gemini-app image found, proceeding..."; \
	fi
	 #docker run -it --rm --name gemini-container2 -v $$PWD:/usr/src/app  --user `id -u`:`id -g`  gemini-app
build:
	 docker build --build-arg USER_ID=$(USER_ID) --build-arg GROUP_ID=$(GROUP_ID) -t gemini-app .

# Test API connectivity and quota
test-api:
	@echo "🧪 Testing Gemini API connectivity..."
	@echo "Command: docker run --rm -v ./:/usr/src/app -e GEMINI_API_KEY=*** gemini-app gemini --help"
	@if docker run --rm -v ./:/usr/src/app -e GEMINI_API_KEY=AIzaSyB647F_VzNA0tT8kacPMLTbL62EWEChmyw gemini-app gemini --help >/dev/null 2>&1; then \
		echo "✅ Gemini CLI is working"; \
		echo "Testing with a simple prompt..."; \
		if docker run --rm -v ./:/usr/src/app -e GEMINI_API_KEY=AIzaSyB647F_VzNA0tT8kacPMLTbL62EWEChmyw gemini-app gemini -y -p "Hello, just testing API connectivity. Please respond with 'OK'"; then \
			echo "✅ API is responsive"; \
		else \
			echo "❌ API test failed - possible quota exceeded or service issue"; \
		fi; \
	else \
		echo "❌ Gemini CLI not working properly"; \
	fi

sh: check-image
	 docker run -it --rm -v ./:/usr/src/app  -e GEMINI_API_KEY=AIzaSyB647F_VzNA0tT8kacPMLTbL62EWEChmyw gemini-app /bin/bash
