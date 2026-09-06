# Правила тестирования

## Инструменты

- **pytest** — для Python-пакетов.
- Структура: тесты в директории `tests/` внутри каждого пакета.

## Что покрывать

- Все публичные функции и методы.
- Edge-cases: пустые входы, невалидные данные, граничные значения.
- Happy path и error path.
- Интеграционные тесты для API-эндпоинтов (FastAPI TestClient).

## Структура тестов

- Имена файлов: `test_<module>.py`.
- Имена классов: `Test<Subject>`.
- Имена функций: `test_<scenario>_<condition>`.
- Arrange-Act-Assert структура (или Given-When-Then).

## Запуск

```bash
make test          # все тесты
make test -- -k "login"  # фильтр по имени
```
