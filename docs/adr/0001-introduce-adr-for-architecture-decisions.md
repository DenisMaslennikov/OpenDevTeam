---
schemaVersion: 0.2.0
id: "0001"
title: "Introduce ADR for architecture decisions"
status: proposed
date: 2026-10-10
deciders: []
tags: [process, documentation]
scope: org
reversibility: two-way-door
blastRadius: org
relatesTo: []
affects: []
provenance:
  authoredBy: human
---

# ADR-0001: Introduce ADR for architecture decisions

## Context

OpenDevTeam активно развивается: формируются роли агентов (team_lead, worker,
reviewer), выбираются инструменты и подходы (DinD, LiteLLM, RabbitMQ, выбор
кодинг-агента для воркеров). Эти решения принимаются в чатах и коммитах, и уже
сейчас нет единого места, где можно увидеть, почему сделан тот или иной выбор и
актуален ли он. По мере роста команды (включая ИИ-агентов) устные решения
теряются, а новые агенты повторяют уже отвергнутые варианты.

## Decision

Будем вести архитектурные решения в формате ADR (Architecture Decision
Record) в каталоге `docs/adr/`, используя инструмент [`@adrkit/cli`](https://adrkit.dev)
(бинарник `adrkit`/`adr`) для создания (`new`), валидации (`lint`) и жизненного
цикла записей (`proposed` → `approve`/`object` → `accept`).

## Options considered

### Option A: ADR через @adrkit/cli (chosen)

| Dimension | Assessment |
|---|---|
| Формат | Структурированный Markdown со schema-фронтом (id, status, date, affects) |
| Инструменты | CLI: new/lint/graph/queue/accept; machine-readable corpus |
| Автоматизация | lint можно встроить в pre-commit/CI; graph строит граф решений |
| Затраты | Один npm-пакет, каталог docs/adr |

### Option B: Простой Markdown-шаблон MADR без инструментов

**Pros:** не требует зависимостей; знакомый формат.
**Cons:** нет валидации структуры, нет статусов/очереди ревью, нет графа
зависимостей решений; качество записей деградирует без lint.

### Option C: Do nothing — решения в README и комментариях к PR

**Pros:** нулевые затраты.
**Cons:** решения размазаны по README/PR/чатам; невозможно проследить историю
и статус решения; ИИ-агентам нечего загрузить как контекст.

## Trade-offs

- Frontmatter со schema — более тяжёлый формат, чем свободный Markdown.
- Нужна дисциплина: каждое значимое решение должно получать запись, иначе
  набор записей неполон и врёт.
- @adrkit/cli — молодой инструмент; при отказе от него записи остаются
  обычным Markdown и переносятся (`migrate --from madr`, ручной перенос).

## Consequences

- Плюсы: новые разработчики и ИИ-агенты получают готовый контекст решений;
  изменения решений прослеживаются через supersedes/relatesTo.
- Минусы: каждое архитектурное решение требует времени на запись и ревью.
- **How we would know this was wrong:** если через 2–3 месяца ADR не создаются
  (число записей не растёт при очевидных архитектурных изменениях) или lint регулярно
  ломается в PR — упрощаем формат или отказываемся от инструмента.
- Revisit if: команда перестаёт следовать процессу propose → review → accept.

## Action items

1. [x] Добавить каталог `docs/adr/` и первые записи.
2. [x] Добавить правило ведения ADR в `.agents/rules/adr.md`.
3. [ ] Встроить `adrkit lint` в pre-commit проверки.
