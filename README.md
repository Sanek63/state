# state

Масштабируемая машина состояний на Python на базе `transitions`.

## Структура проекта

- `state_machine/dto.py`  
  Базовые DTO: описание узлов и графа (`WorkflowDTO`, `TriggerNodeDTO`, `TriggerRoutesDTO`),
  а также контекст и результат выполнения триггера.

- `state_machine/triggers.py`  
  Базовый контракт триггера (`BaseTrigger`) и простые универсальные триггеры для базовых сценариев.

- `state_machine/engine.py`  
  Ядро машины состояний (`StatefulWorkflow`):
  - валидирует граф,
  - валидирует наличие фабрик триггеров,
  - регистрирует переходы,
  - выполняет пошаговый прогон (`step`) и полный прогон (`run`),
  - поддерживает сброс в начальное состояние (`reset`).

- `state_machine/skill_routing.py`  
  Прикладная схема роутинга скиллов:
  - `SkillRoutingContextDTO` — контекст доменной логики,
  - `build_skill_routing_workflow()` — декларативное описание графа узлов,
  - `build_skill_routing_trigger_factories()` — привязка ключей узлов к триггерам,
  - `build_skill_routing_state_machine()` — сборка готовой машины состояний.

- `tests/test_state_machine.py`  
  Тесты общего движка и маршрутизации `YES/NO`.

- `tests/test_skill_routing_scheme.py`  
  Тесты прикладного сценария роутинга скиллов.

## Что реализовано

- Декларативное описание графа состояний через DTO.
- Отделение доменной логики триггеров от универсального движка.
- Динамическая маршрутизация (`YES` / `NO`).
- Возможность переопределять маршруты узлов при сборке workflow.
- Полностью покрытые тестами ключевые ветки прикладной схемы.

## Установка

```bash
pip install -r requirements.txt
```

## Запуск тестов

```bash
python -m unittest discover -s tests -p 'test_*.py'
```
