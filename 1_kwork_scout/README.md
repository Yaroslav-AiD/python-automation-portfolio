# Kwork Scout

Парсер заказов с фриланс-биржи Kwork по ключевым словам.

Скрипт открывает страницу проектов Kwork, находит все заказы и фильтрует их по заданным ключевым словам (парсинг, автоматизация, боты, Google Sheets, Wildberries и др.). Подходящие заказы сохраняются в JSON-файл.

## Как работает
- Selenium WebDriver открывает страницу https://kwork.ru/projects
- Находит все ссылки на проекты
- Фильтрует по ключевым словам в названии
- Сохраняет результат в `kwork_orders.json`

## Запуск
```bash
python kwork_scout.py

## Зависимости

  Python 3.12
  Selenium
  Chrome WebDriver

## Установка:
pip install selenium

## Вывод

KWORK SELENIUM PARSER
Найдено ссылок на проекты: 16
✅ Сделать дизайн для карточек Wildberries...
✅ Поменять оформление в Google Sheets таблицах...
✅ Логотип для ТГ-бота...
📁 Сохранено 4 заказов в kwork_orders.json

Запуск на Windows

1. Установите Python с [python.org](https://python.org) (отметьте "Add Python to PATH")
2. Установите Selenium:
   ```cmd
   pip install selenium
