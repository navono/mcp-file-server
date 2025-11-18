IMAGE_NAME = mcp-file-server:latest

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

.PHONY: build start stop