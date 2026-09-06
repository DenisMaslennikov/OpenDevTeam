# Архитектурные принципы

## Разделение ответственности

1. **Backend (`packages/backend/`)** — только FastAPI API управления проектом: CRUD задач, сессий, выбор тестов пользователем. Не содержит логики оркестрации.
2. **Team Lead (`packages/agents/team_lead/`)** — агент-оркестратор: граф диалога, постановка задач, пуш задач в очередь RabbitMQ, генерация ключей для агентов. Не путать с backend. Не запускает поды напрямую.
3. **Агенты** — долгоживущие Deployment-поды с DinD, берут задачи из очереди RabbitMQ, живут ограниченное время (`AGENT_LIFETIME`). Воркер (`packages/agents/worker/`) — один агент с режимами `WORKER_MODE=researcher|coder`. Протоколы ответов хранятся в папке каждого агента.
4. **Core (`packages/agents/core/`)** — общее переиспользуемое: LangGraph утилы, watchdog, litellm-клиент, rabbitmq-консьюмер.

## Очередь задач (RabbitMQ)

- Тимлид — единственный продюсер задач; воркеры и ревьюер — консьюмеры.
- Очереди по типу работы: `tasks.researcher`, `tasks.coder`, `tasks.reviewer`.
- Сообщение задачи содержит `task_id`, `session_id`, `repo_url`, `litellm_api_key` (виртуальный ключ на задачу), режимный пейлоад.
- Воркеры живут ограниченное время (`AGENT_LIFETIME`, по умолчанию 1 час): по истечении корректно завершаются, k8s перезапускает под. Перед завершением не берут новые задачи.
- Подтверждение (ack) после завершения обработки; при падении задача возвращается в очередь.
- Клиент — `aio-pika` (общий модуль в core).

## LiteLLM

- **Один инстанс** на всех агентов.
- У каждого агента свой виртуальный ключ, который тимлид генерирует через LiteLLM и передаёт в сообщении задачи.
- Общий командный API-ключ провайдера LLM хранится в k8s Secret `litellm-secrets`.
- Гибридный режим: локальные модели (GLM 5.2) + облачные провайдеры + прокси.
- LiteLLM обеспечивает: fallback, retry, spend tracking, rate limiting.

## Git-доступ

- Через SSH-ключ и API-токены провайдеров (GitHub/GitLab), общие на всю команду.
- Хранятся в k8s Secret `git-secrets` (`ssh-private-key`, `ssh-known-hosts`, `github-token`, `gitlab-token`, `git-user-name`, `git-user-email`).
- Оркестратор монтирует ключ и токены в под агента при запуске, URL репо передаёт через env.

## Watchdog

- Модуль в `packages/agents/core/` для детекта зависаний и зацикливаний LLM-сессий.
- Дополняет LiteLLM: LiteLLM ловит сетевые/API-ошибки, watchdog — логические зависания.
- При срабатывании перезапускает сессию агента.

## Docker-in-Docker (DinD)

- Каждый агент-воркер запускается в поде k8s с sidecar-контейнером DinD: два контейнера в поде — `dind` и сам агент (Python-скрипт).
- **Dev-контур (k3d):** образ `docker:dind`, `privileged: true`, storage driver `overlay2`, bridge-нетворкинг + NAT работают полностью. Compromise принят осознанно: привилегированный под = root на ноде k3d, допустимо только внутри одноразового dev-кластера (граница — WSL2 VM). Воркеры исполняют LLM-сгенерированный код — на прод такой вариант не переносим.
- **Прод: требуется Sysbox** — ноды с runtime `sysbox-runc` (`runtimeClassName: sysbox-runc` в манифестах), обычный `docker:dind` без `privileged`, полноценные userns-изоляция и bridge. Rootless dind (`docker:dind-rootless`) — только fallback там, где Sysbox недоступен.
- dockerd слушает только `tcp://127.0.0.1:2375` (loopback пода, наружу ничего не пробрасывается). Агент подключается через `DOCKER_HOST=tcp://127.0.0.1:2375`.
- Реестр-зеркало: `--registry-mirror=http://cache:5000` (pull-through кеш Docker Hub).
- Fallback-цепочка storage driver: `overlay2` → `fuse-overlayfs` (нужен `/dev/fuse`). `vfs` не используется (нет дедупликации слоёв — недопустимый рост диска на 5 воркерах).
