IMAGE_NAME = mcp-file-server:streaming
HTTP_PROXY ?= http://172.18.32.1:18899
HTTPS_PROXY ?= http://172.18.32.1:18899
NO_PROXY ?=

# 可以在这里定义颜色变量，防止 echo 报错 (如果之前未定义)
YELLOW=\033[1;33m
GREEN=\033[0;32m
NC=\033[0m

build: ## Build the runtime Docker image (default)
	@echo "$(YELLOW)Building runtime Docker image as $(IMAGE_NAME)...$(NC)"
	# 将 IMAGE_NAME 作为环境变量传递给 docker compose
	IMAGE_NAME=$(IMAGE_NAME) docker compose build --build-arg HTTP_PROXY=$(HTTP_PROXY) --build-arg HTTPS_PROXY=$(HTTPS_PROXY) --build-arg NO_PROXY=$(NO_PROXY)
	@echo "$(GREEN)Runtime image built successfully!$(NC)"

start:
	@echo "$(YELLOW)Starting runtime Docker container...$(NC)"
	# 启动时同样传递变量，确保使用正确的镜像名
	IMAGE_NAME=$(IMAGE_NAME) docker compose up -d
	@echo "$(GREEN)Runtime container started successfully!$(NC)"

stop:
	@echo "$(YELLOW)Stopping runtime Docker container...$(NC)"
	docker compose down
	@echo "$(GREEN)Runtime container stopped successfully!$(NC)"

.PHONY: build start stop