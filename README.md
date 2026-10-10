# OpenDevTeam

Система для агентской ИИ-разработки. В первой итерации — автоматическое написание тестов для кода. Система ориентирована на запуск в Kubernetes.

## Концепция

Оркестратор (**тимлид**) общается с пользователем, предлагает какие тесты стоит реализовать, получает выбор пользователя и на его основе ставит задачи в **очередь RabbitMQ**. Воркеры и ревьюеры — долгоживущие поды Kubernetes, которые берут задачи из очереди, работают ограниченное время (`AGENT_LIFETIME`) и завершаются. Каждый агент имеет свой Docker-in-Docker контейнер для поднятия зависимостей и запуска тестов.

### Типы агентов

| Агент | Роль |
|---|---|
| **Team Lead** (оркестратор) | Диалог с пользователем, постановка задач, пуш в очередь RabbitMQ, генерация ключей |
| **Worker** (воркер) | Долгоживущий под. Берёт задачи из очереди, работает в режимах `researcher` или `coder` через `WORKER_MODE` |
| **Reviewer** (ревьюер) | Долгоживущий под. Берёт задачи на проверку из очереди, JSON-вердикт |

## Архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│                        Kubernetes Cluster                       │
│                                                                 │
│  ┌──────────┐    ┌──────────────────┐    ┌──────────────────┐  │
│  │ Frontend │◄──►│   Backend (API)  │◄──►│   PostgreSQL     │  │
│  │ React+   │    │   FastAPI        │    │   (задачи,       │  │
│  │ Antd 6   │    │   управление     │    │    сессии, ключи)│  │
│  └──────────┘    │   проектом       │    └──────────────────┘  │
│                  └────────┬─────────┘                          │
│                  ┌────────▼──┐                                 │
│                  │ Team Lead  │                                 │
│                  │ (оркестр.) │                                 │
│                  │ LangGraph  │                                 │
│                  └──────┬─────┘                                 │
│                         │ пушит задачи                           │
│                  ┌──────▼─────┐                                  │
│                  │  RabbitMQ  │ ◄─── берут задачи                │
│                  │ (очередь)  │                                  │
│                  └──────┬─────┘                                  │
│           ┌─────────────┼─────────────┐                          │
│           ▼             ▼             ▼                          │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │   Worker     │ │   Worker     │ │  Reviewer    │            │
│  │ (researcher) │ │   (coder)    │ │  (долгожив.  │            │
│  │ (долгожив.   │ │ (долгожив.   │ │   под)       │            │
│  │  Deployment) │ │  Deployment) │ │              │            │
│  │              │ │              │ │              │            │
│  │ ┌──────────┐ │ │ ┌──────────┐ │ │              │            │
│  │ │  DinD    │ │ │ │  DinD    │ │ │              │            │
│  │ │ (Docker) │ │ │ │ (Docker) │ │ │              │            │
│  │ └──────────┘ │ │ └──────────┘ │ │              │            │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘            │
│         │                │                │                      │
│         └────────────────┼────────────────┘                     │
│                          ▼                                      │
│                ┌──────────────────┐                            │
│                │   LiteLLM Proxy  │  ◄── 1 на всех агентов      │
│                │   (гибрид:       │      ключи, fallback,       │
│                │    локальные +   │      retry, spend tracking, │
│                │    облачные)     │      watchdog               │
│                └──────────────────┘                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼ git push (branch → PR)
              ┌──────────────────────┐
              │  Внешний git-репо    │
              │  (GitHub/GitLab/...)│
              └──────────────────────┘
```

## Поток работы (MVP)

1. Пользователь в UI подключает git-URL репо + deploy token.
2. Тимлид клонирует репо → пушит задачу в очередь RabbitMQ → воркер в режиме `researcher` берёт её → JSON-отчёт о коде.
3. Тимлид через UI предлагает список тестов к реализации → пользователь выбирает.
4. Тимлид пушит задачи в очередь → воркеры в режиме `coder` берут их (DinD: зависимости, тесты, git push branch) → ревьюер берёт задачу на проверку.
5. LiteLLM + watchdog ловят зависания/зацикливания → перезапуск сессии агента.
6. PR во внешний репо + статус в UI.

## Стек

| Слой | Технологии |
|---|---|
| Backend (API) | Python 3.14, FastAPI, Pydantic v2, uv |
| Team Lead (оркестратор) | Python 3.14, LangGraph, aio-pika, uv |
| Агенты (общая база) | Python 3.14, LangGraph, aio-pika, uv, Docker-in-Docker |
| LLM-шлюз | LiteLLM proxy (гибрид: локальный GLM 5.2 + облачные + прокси) |
| БД | PostgreSQL (задачи, сессии, ключи, токен-статистика) |
| Очередь задач | RabbitMQ (aio-pika; воркеры берут задачи, тимлид пушит) |
| Фронтенд | React 19, Vite, TypeScript, Ant Design 6, TanStack Query |
| Инфра | Kubernetes (k3d для dev), Skaffold, Docker BuildKit |
| Кодер-движок | TBD — абстракция в worker, тестим aider vs opencode |
| Git | внешний репо (без внутреннего сервера) |

## Структура проекта

```
OpenDevTeam/
├── README.md
├── AGENTS.md                          # инструкции для AI при работе с репо
├── opencode.json                      # конфиг opencode (загрузка правил)
├── .agents/                           # рабочее пространство opencode (dev-time)
│   └── rules/                         # dev-правила (workflow, code-style, testing, ...)
├── packages/
│   ├── backend/                       # FastAPI API для управления проектом
│   ├── agents/
│   │   ├── core/                      # общее переиспользуемое (LangGraph утилы, watchdog, litellm-клиент, rabbitmq-консьюмер)
│   │   ├── team_lead/                 # ОРКЕСТРАТОР (тимлид) — пушит задачи в очередь
│   │   ├── worker/                    # воркер (режимы: researcher, coder) — берёт задачи из очереди
│   │   └── reviewer/                  # ревьюер — берёт задачи из очереди
│   └── frontend/                      # React + Vite + TS + Ant Design 6
├── deploy/
│   └── k8s/                           # манифесты
├── docker/                            # Docker-образы (каждый в своей папке)
│   ├── agents/                        # общие .env + .env.example для всех агентов
│   ├── backend/                       # Dockerfile + .env + .env.example
│   ├── team_lead/                     # Dockerfile + .env + .env.example
│   ├── worker/                        # Dockerfile + .env + .env.example (только личные)
│   ├── reviewer/                     # Dockerfile + .env + .env.example (только личные)
│   ├── litellm/                       # Dockerfile + litellm-config.yaml + .env + .env.example
│   ├── frontend/                     # Dockerfile (Vite dev-сервер)
│   └── cache/                         # Docker registry pull-through cache + .env + .env.example
├── skaffold.yaml                      # Skaffold: сборка + импорт в k3d + деплой
├── Makefile
└── .gitignore
```

## Переменные окружения

Каждый Docker-образ имеет собственные `.env` и `.env.example` в своей папке (`docker/<service>/`). Переменные не общие — каждый сервис получает только то, что ему нужно.

Для агентов-воркеров (worker, reviewer) общие переменные вынесены в `docker/agents/`, в личных `.env` остаются только специфичные для агента:

| Папка | Сервис | Переменные |
|---|---|---|
| `docker/agents/` | **Общие для всех агентов** | `LITELLM_BASE_URL`, `RABBITMQ_URL`, `LLM_TIMEOUT`, `SESSION_TIMEOUT`, `AGENT_LIFETIME`, `LOG_LEVEL` |
| `docker/backend/` | FastAPI API | `DATABASE_URL`, `LITELLM_BASE_URL`, `LOG_LEVEL` |
| `docker/team_lead/` | Оркестратор | `DATABASE_URL`, `LITELLM_BASE_URL`, `RABBITMQ_URL`, `LITELLM_API_KEY`, `LOG_LEVEL` |
| `docker/worker/` | Воркер (researcher/coder) | `WORKER_MODE`, `DOCKER_HOST`, `CODER_ENGINE` |
| `docker/reviewer/` | Ревьюер | `SESSION_TIMEOUT=900` (переопределяет общую) |
| `docker/litellm/` | LiteLLM proxy | `LITELLM_MASTER_KEY`, `LLM_API_KEY`, `DATABASE_URL` |
| `docker/cache/` | Docker registry cache | `CACHE_REGISTRY_URL` |

Локальный запуск агента — оба файла, последний переопределяет:

```bash
docker run --env-file docker/agents/.env --env-file docker/worker/.env opendevteam/worker:latest
```

В k8s общие переменные приходят из ConfigMap `agents-common-config`. Динамические данные задачи (`TASK_ID`, `SESSION_ID`, `LITELLM_API_KEY`, `REPO_URL`) приходят **в сообщении из очереди RabbitMQ**, а не через env. Воркеры живут ограниченное время (`AGENT_LIFETIME`, по умолчанию 1 час) и завершаются после истечения.

Git-доступ — через SSH-ключ и API-токены провайдеров (GitHub/GitLab), общие на всю команду. Хранятся в k8s Secret `git-secrets` (`ssh-private-key`, `ssh-known-hosts`, `github-token`, `gitlab-token`, `git-user-name`, `git-user-email`). Оркестратор монтирует ключ и токены в под агента при запуске, URL репо передаёт через env.

LiteLLM — у каждого агента свой виртуальный ключ, который тимлид генерирует через LiteLLM и передаёт в сообщении задачи. Общий командный API-ключ провайдера LLM хранится в `litellm-secrets`.

`.env.example` — шаблон (коммитится в репо). `.env` — реальные значения (в `.gitignore`, не коммитится).

## Быстрый старт

### Требования

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) (менеджер пакетов)
- Node.js 22+ (для фронтенда)
- Docker + Docker BuildKit
- [k3d](https://k3d.io/) + kubectl (dev-кластер)
- [Skaffold](https://skaffold.dev/) v2+

### Dev-контур (k3d + Skaffold)

Разработка ведётся в Kubernetes: все сервисы (backend с `uvicorn --reload`, frontend на Vite dev-сервере, инфраструктура) крутятся в кластере k3d. Skaffold собирает образы, импортирует их в кластер (`k3d image import`), применяет манифесты и пробрасывает порты.

```bash
# Полный цикл: сборка + импорт + деплой + port-forward (Ctrl+C — cleanup)
# Кластер k3d создаётся автоматически при первом запуске
make dev

# Остановить поды (кластер и импортированные образы остаются)
make stop

# Полный снос dev-контура: кластер + DinD-данные воркеров
make reset

# Порт-форварды: frontend http://localhost:5173, backend http://localhost:8000, RabbitMQ UI http://localhost:15672
```

Агенты (team-lead, worker, reviewer) — заглушки: печатают `[<agent>] agent not yet implemented — idling` и остаются живыми в idle-цикле (иначе skaffold dev воспринимает exit != 0 как провал деплоя и откатывает весь dev-контур). Это ожидаемо, пока нет кода. Воркеры — 5 реплик, у каждого пода два контейнера: `dind` (Docker-in-Docker, storage driver `overlay2`, bridge-нетворкинг + NAT, слушает только `127.0.0.1:2375` внутри пода) и `worker`.

### Безопасность dev-контура (компромисс: privileged DinD)

В dev-контуре dind-сайдкар воркеров/ревьюера запускается как `privileged: true` (образ `docker:dind`, `overlay2`, полный bridge-нетворкинг). Это осознанный компромисс: rootless-вариант в k3d-в-WSL2 требует `--bridge=none --storage-driver=vfs`, что неприемлемо (vfs не дедуплицирует слои — недопустимый рост диска на 5 воркерах).

Риски:

- privileged-под ≈ **root на ноде k3d** (все CAP_\*, seccomp/AppArmor off, host `/dev`; доступ к блочным устройствам, загрузка модулей ядра);
- ноды k3d сами запускаются Docker'ом с `--privileged`: на **голом Linux** это эквивалент root на dev-машине (`~/.ssh`, git-креды, kubeconfig); на **WSL2** граница — VM, но из неё доступны `/mnt/c` (чтение/запись файлов Windows) и interop (запуск `.exe`);
- доступ к Docker API dind = root, а агенты исполняют LLM-сгенерированный и чужой код из репо — prompt-injection / вредоносный репо это реалистичный путь эскейпа (`docker run --privileged` внутри dind);
- seccomp unconfined: kernel-эскейпы не блокируются;
- 5×DinD с overlay2: расход диска на кеш образов, runaway-билды.

Правила гигиены: dev-кластер одноразовый (`k3d cluster delete` при подозрении на компрометацию), в `git-secrets`/`litellm-secrets` только dev-значения, не направлять агентов на недоверенные репо до перехода на Sysbox.

> **Продакшен: требуется Sysbox.** Ноды с runtime `sysbox-runc` (`runtimeClassName: sysbox-runc` в манифестах), обычный `docker:dind` **без** `privileged`: полноценная userns-изоляция, bridge-нетворкинг и overlay внутри. Rootless dind (`docker:dind-rootless`) — только fallback там, где Sysbox недоступен.

Альтернатива без Skaffold:

```bash
docker build -f docker/backend/Dockerfile -t opendevteam/backend:latest .   # и т.д. для остальных образов
k3d image import opendevteam/backend:latest -c dev-cluster                  # импорт каждого образа
kubectl apply -f deploy/k8s/                                               # применить манифесты
```

### Локальная разработка

```bash
# Установить зависимости backend + агентов
make install

# Линтинг и типизация
make lint
make typecheck

# Тесты
make test
```

### Фронтенд

Фронтенд разрабатывается как Vite dev-сервер в контейнере (Skaffold/k8s). Локально:

```bash
cd packages/frontend
npm install
npm run dev
```

> **npm-зеркало:** в `packages/frontend/.npmrc` указано зеркало `https://registry.npmmirror.com/` — официальный registry.npmjs.org и зеркало gitverse нестабильно доступны из этой сети (503/таймауты). Если у вас нормальный доступ к npmjs, удалите или замените строку `registry=` в `.npmrc`.

## Лицензия

TBD
