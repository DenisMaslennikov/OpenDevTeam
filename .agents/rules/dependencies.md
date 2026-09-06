# Управление зависимостями

## Менеджер пакетов

- **Python:** `uv` (workspace). Корневой `pyproject.toml` объявляет workspace, пакеты в `packages/*`.
- **Frontend:** `npm`.

## Версии

**Всегда выбирай новейшую стабильную версию** пакета при добавлении. Проверяй актуальную версию в репозитории пакета (PyPI, npm) и документации.

- В `pyproject.toml` не пинжируй версии жёстко — указывай без версии (берётся последняя) или с нижней границей `>=x.y` только при необходимости.
- В `package.json` используй caret-диапазоны (`^x.y.z`) или `latest`.
- Исключение: жёсткое пинжирование только при веской причине (security, breaking change).

## Добавление Python-пакета

```bash
# Добавить в конкретный workspace-пакет
uv add --package <package-name> <dependency>

# Добавить в корень
uv add <dependency>
```

## Добавление npm-пакета

```bash
cd packages/frontend
npm install <package>
```
