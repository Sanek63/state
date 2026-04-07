# state

Масштабируемая машина состояний на Python на базе `transitions`.

## Что реализовано

- DTO для описания графа состояний, контекста и результата выполнения триггера.
- Отдельные классы триггеров со своей логикой (`YES`, `NO`, `DEFAULT`).
- Динамическая маршрутизация между узлами: связи задаются через `WorkflowDTO`.
- Движок `StatefulWorkflow`, который выполняет переходы через библиотеку `transitions`.
- Реализована прикладная схема роутинга скиллов из диаграммы:
  `state_machine/skill_routing.py` (`SkillRoutingContextDTO`, сборка workflow, триггеры узлов).

## Установка

```bash
pip install -r requirements.txt
```

## Запуск тестов

```bash
python -m unittest discover
```
