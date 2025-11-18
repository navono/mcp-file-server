IMAGE_NAME = mcp-file-server:streaming
HTTP_PROXY ?=http://172.18.32.1:18899
HTTPS_PROXY ?=http://172.18.32.1:18899
NO_PROXY ?=

build: ## Build the runtime Docker image (default)
	@echo "$(YELLOW)Building runtime Docker image...$(NC)"
	docker compose build --build-arg HTTP_PROXY=$(HTTP_PROXY) --build-arg HTTPS_PROXY=$(HTTPS_PROXY) --build-arg NO_PROXY=$(NO_PROXY)
	@echo "$(GREEN)Runtime image built successfully!$(NC)"

start:
	@echo "$(YELLOW)Starting runtime Docker container...$(NC)"
	docker compose up -d
	@echo "$(GREEN)Runtime container started successfully!$(NC)"

stop:
	@echo "$(YELLOW)Stopping runtime Docker container...$(NC)"
	docker compose down
	@echo "$(GREEN)Runtime container stopped successfully!$(NC)"

start-streaming:
	@echo "$(YELLOW)Starting streaming HTTP Docker container...$(NC)"
	docker compose run -d --name $(IMAGE_NAME)-streaming -p 8001:8001 mcp-file-server uv run python streaming_server.py
	@echo "$(GREEN)Streaming HTTP container started successfully!$(NC)"

stop-streaming:
	@echo "$(YELLOW)Stopping streaming HTTP Docker container...$(NC)"
	- docker stop $(IMAGE_NAME)-streaming >/dev/null 2>&1 || true
	- docker rm $(IMAGE_NAME)-streaming >/dev/null 2>&1 || true
	@echo "$(GREEN)Streaming HTTP container stopped successfully!$(NC)"

.PHONY: build start stop start-streaming stop-streaming