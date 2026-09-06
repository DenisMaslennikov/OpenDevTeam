.DEFAULT_GOAL := help
.PHONY: install dev stop reset lint format typecheck test clean help

UV := uv
CLUSTER := dev-cluster

help: ## Показать список доступных команд
	@awk 'BEGIN {FS = ":.*##"; printf "Команды OpenDevTeam:\n"} \
	/^[a-zA-Z_-]+:.*##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

install: ## Установка зависимостей (uv workspace)
	$(UV) sync --all-packages

dev: ## Dev-контур: k3d + skaffold (сборка + деплой + port-forward)
	@k3d cluster get $(CLUSTER) >/dev/null 2>&1 || k3d cluster create $(CLUSTER) --agents 1
	skaffold dev

stop: ## Остановить поды (кластер и образы остаются)
	skaffold delete

reset: ## Полный снос dev-кластера
	-$(MAKE) stop
	k3d cluster delete $(CLUSTER)

lint: ## Линтинг (ruff)
	$(UV) run ruff check .

format: ## Форматирование (ruff)
	$(UV) run ruff format .

typecheck: ## Типизация (mypy)
	$(UV) run mypy --strict packages/

test: ## Тесты (pytest)
	$(UV) run pytest

clean: ## Очистка кешей
	$(UV) run ruff clean
	find . -type d -name __pycache__ -exec rm -rf {} +
