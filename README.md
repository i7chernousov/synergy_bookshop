# Synergy Bookshop — веб-версия книжного магазина (Django)

Реализовано по Кейс-задаче №4:
- Два интерфейса: **пользовательский** (каталог, фильтры/сортировка, покупка/аренда) и **админский** (Django Admin + /dashboard/).
- База любимых книг (авторы, категории, книги).
- Просмотр книги и статуса доступности.
- Сортировка/фильтры по **категории**, **автору**, **году написания**.
- **Покупка** или **аренда** на 2 недели / 1 месяц / 3 месяца.
- Для администратора: управление книгами/ценами/статусами/наличием, автоматические **напоминания** об окончании аренды (через cron-команду).

## Быстрый старт
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py seed_demo         # создаст admin/ivan/olga (пароль: password), авторов/категории/книги
python manage.py runserver
```
Откройте http://127.0.0.1:8000/. Вход в админку: `/admin/` (admin/password).

## Напоминания об аренде
Команда:
```bash
python manage.py send_rental_reminders
```
По умолчанию письма выводятся в консоль (EMAIL_BACKEND=console). Для реальной отправки укажите SMTP-настройки.

**Автоматизация (cron, ежедневно 9:00):**
```cron
0 9 * * * /path/to/venv/bin/python /path/to/project/manage.py send_rental_reminders
```

## Полезные URL
- `/` — каталог с фильтрами и сортировкой
- `/books/<id>/` — страница книги (покупка/аренда)
- `/my/orders/` — ваши заказы
- `/dashboard/` — простой дашборд для сотрудников (требует is_staff)
- `/admin/` — полная админка

## Модели
- `Author`, `Category`, `Book(status, available_copies, цены)`
- `Order`, `OrderItem(kind=purchase|rental, duration, start_date, end_date)`

Доступность книги учитывает активные аренды (до даты окончания). Покупка уменьшает `available_copies`.

## Настройка времени и языка
TIME_ZONE=`Europe/Riga`, LANGUAGE_CODE=`ru-ru`.
