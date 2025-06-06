# Warehouse Management System

Проект чистый склад: реализация функционала создания продуктов, добавления в заказ на складе и тестирование всего функционала. 
Используемый стек и подход: python 3.10, pytest, DDD and Clean Architecture

## Установка

Этот проект использует `uv` для управления зависимостями и виртуальным окружением.

1.  **Установите `uv`**
    Если у вас еще не установлен `uv`, следуйте [официальной инструкции по установке uv](https://github.com/astral-sh/uv#installation). 
    
    `uv` — это очень быстрый установщик пакетов и менеджер виртуальных окружений для Python.

2.  **Клонируйте репозиторий**
    ```bash
    git clone git@github.com:vasevooo/warehouse.git
    cd otus-hw 
    ```

3.  **Создайте и активируйте виртуальное окружение с помощью `uv`**
    `uv` может создать виртуальное окружение для вас. Находясь в корневой директории проекта (`otus-hw`):
    ```bash
    uv venv
    ```
    Эта команда создаст виртуальное окружение с именем `.venv` в текущей директории (если оно еще не существует) и автоматически использует Python, указанный в `requires-python` вашего `pyproject.toml` (или ваш системный Python, если он совместим).

    Затем активируйте созданное окружение:
    *   Для macOS/Linux:
        ```bash
        source .venv/bin/activate
        ```
    Вы поймете, что окружение активно, если в начале вашей командной строки появится `(.venv)`.

4.  **Установите/синхронизируйте зависимости**
    Теперь, когда виртуальное окружение активно, установите все необходимые зависимости (включая те, что нужны для разработки) с помощью `make`:
    ```bash
    make sync-deps
    ```
    Эта команда использует `uv pip install -E dev .` для установки пакетов, указанных в `pyproject.toml`.
    
    Если вы используете pre-commit хуки (рекомендуется), установите их после синхронизации зависимостей:
    ```bash
    pre-commit install
    ```## Установка


## Использование (Примеры "боевого" запуска)

Проект предоставляет CLI для взаимодействия со складом через `main.py`. Вы можете использовать `make` для удобства.

### Создание нового продукта
```bash
make create-product name="Super Laptop" qty=10 price=1250.50
# или напрямую:
# python3 main.py create-product --name="Super Laptop" --quantity=10 --price=1250.50
```

### Создание нового заказа
Для создания заказа укажите товары и их количество в формате `id1,qty1;id2,qty2;...`. ID продуктов можно узнать из списка продуктов.
```bash
make create-order items="1,2;2,1" 
# Пример: заказать 2 шт. продукта с ID=1 и 1 шт. продукта с ID=2
# или напрямую:
# python3 main.py create-order --items="1,2;2,1"
```

### Просмотр списка всех продуктов
```bash
make list-products
# или напрямую:
# python3 main.py list-products
```

## Запуск тестов

Для запуска всех тестов:
```bash
make test
```

Для запуска тестов с отчетом о покрытии кода:
```bash
make coverage
```
Отчет в формате HTML будет доступен в директории `htmlcov/`.

## Линтинг и форматирование

Для проверки кода линтером (Ruff):
```bash
make lint
```

Для автоматического форматирования кода (Ruff):
```bash
make format
```
