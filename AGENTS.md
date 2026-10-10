# AGENTS.md

Инструкции для AI-агентов (включая opencode), работающих с этим репозиторием.

## Обзор проекта

OpenDevTeam — система для агентской ИИ-разработки. MVP: автоматическое написание тестов для кода. Система запускается в Kubernetes: оркестратор (тимлид) ставит задачи и пушит их в очередь RabbitMQ. Воркеры и ревьюеры — долгоживущие поды, которые берут задачи из очереди и работают ограниченное время (`AGENT_LIFETIME`). Каждый агент имеет Docker-in-Docker для запуска проекта и тестов. LLM-доступ — через общий LiteLLM proxy.

## Структура пакетов

| Путь | Назначение |
|---|---|
| `packages/backend/` | FastAPI API для управления проектом (НЕ агент) |
| `packages/agents/core/` | Общее переиспользуемое агентами (LangGraph утилы, watchdog, litellm-клиент, rabbitmq-консьюмер) |
| `packages/agents/team_lead/` | Оркестратор (тимлид) — пушит задачи в очередь |
| `packages/agents/worker/` | Агент-воркер (режимы: researcher, coder) — берёт задачи из очереди |
| `packages/agents/reviewer/` | Агент-ревьюер — берёт задачи из очереди |
| `packages/frontend/` | React + Vite + TS + Ant Design 6 |

## Docker-образы и переменные окружения

Каждый Docker-образ живёт в своей папке `docker/<service>/` вместе с `Dockerfile`, `.env` и `.env.example`. Переменные окружения **не общие** — каждый сервис получает только то, что ему нужно. `.env.example` — шаблон (коммитится), `.env` — реальные значения (в `.gitignore`, не коммитится).

Для агентов-воркеров (worker, reviewer) общие переменные вынесены в `docker/agents/`, в личных `.env` остаются только специфичные для агента. Локальный запуск — `--env-file docker/agents/.env --env-file docker/<agent>/.env` (последний переопределяет).

| Папка | Переменные |
|---|---|
| `docker/agents/` | **Общие для всех агентов:** `LITELLM_BASE_URL`, `RABBITMQ_URL`, `LLM_TIMEOUT`, `SESSION_TIMEOUT`, `AGENT_LIFETIME`, `LOG_LEVEL` |
| `docker/backend/` | `DATABASE_URL`, `LITELLM_BASE_URL`, `LOG_LEVEL` |
| `docker/team_lead/` | + `LITELLM_API_KEY` |
| `docker/worker/` | `WORKER_MODE`, `DOCKER_HOST`, `CODER_ENGINE` |
| `docker/reviewer/` | + `SESSION_TIMEOUT=900` (переопределяет общую) |
| `docker/litellm/` | `LITELLM_MASTER_KEY`, `LLM_API_KEY`, `DATABASE_URL` |
| `docker/cache/` | `CACHE_REGISTRY_URL` |
| `docker/frontend/` | (нет переменных, Vite dev-сервер) |

Git-доступ — через SSH-ключ и API-токены провайдеров (GitHub/GitLab), общие на всю команду. Хранятся в k8s Secret `git-secrets` (`ssh-private-key`, `ssh-known-hosts`, `github-token`, `gitlab-token`, `git-user-name`, `git-user-email`). Оркестратор монтирует в под агента при запуске, URL репо передаёт через env.

LiteLLM — у каждого агента свой виртуальный ключ, который тимлид генерирует через LiteLLM и передаёт в сообщении задачи. Общий командный API-ключ провайдера LLM хранится в `litellm-secrets`.

## Команды

```bash
make install         # установка зависимостей (uv workspace)
make dev             # dev-контур: k3d + skaffold (сборка + деплой + port-forward, автосоздание кластера)
make stop            # остановить поды (кластер и образы остаются)
make reset           # полный снос dev-кластера
make lint            # линтинг (ruff)
make format          # форматирование (ruff)
make typecheck       # типизация (mypy)
make test            # тесты (pytest)
make clean           # очистка кешей
```

Dev-контур (k3d + Skaffold) запускается через `make dev` (обёртка над `skaffold dev`). Прямые команды skaffold:

```bash
skaffold build       # только сборка + импорт в k3d
skaffold run         # разовый деплой без слежения
```

Порт-форварды: frontend `http://localhost:5173`, backend `http://localhost:8000`, RabbitMQ UI `http://localhost:15672`.

Фронтенд: `cd packages/frontend && npm install && npm run dev` (в `.npmrc` указано зеркало `registry.npmmirror.com` — см. README).

## Файлы правил

Подробные правила разработки разделены по смыслу в `.agents/rules/`. Загружаются через `opencode.json` → `instructions`.

| Файл | Содержание |
|---|---|
| `.agents/rules/workflow.md` | Процесс разработки: git, ветки, коммиты, pre-commit проверки |
| `.agents/rules/code-style.md` | Конвенции кода: Python 3.14, ruff, типизация, именование, docstrings |
| `.agents/rules/testing.md` | Правила тестирования: pytest, структура тестов, что покрывать |
| `.agents/rules/dependencies.md` | Управление зависимостями: uv, версии, добавление пакетов |
| `.agents/rules/architecture.md` | Архитектурные принципы: backend vs team_lead, RabbitMQ, LiteLLM, DinD, watchdog |
| `.agents/rules/documentation.md` | Правила документации: обновление AGENTS.md/README.md при изменениях |

## Runtime-правила агентов

Правила для runtime-агентов системы (не для разработки проекта) будут храниться рядом с кодом каждого агента в `packages/agents/<name>/rules/`. Будут написаны позже.
