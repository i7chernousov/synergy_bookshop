    from datetime import timedelta
    from django.core.management.base import BaseCommand
    from django.utils import timezone
    from django.core.mail import send_mail
    from django.contrib.auth.models import User
    from store.models import OrderItem

    class Command(BaseCommand):
        help = 'Отправляет напоминания пользователям об окончании срока аренды.'

        def handle(self, *args, **kwargs):
            today = timezone.now().date()
            thresholds = {
                'За 3 дня до окончания': today + timedelta(days=3),
                'За 1 день до окончания': today + timedelta(days=1),
                'Просрочено': today - timedelta(days=1),
            }

            count = 0

            # За 3 и 1 день до окончания
            for label, target_date in [('За 3 дня до окончания', thresholds['За 3 дня до окончания']),
                                       ('За 1 день до окончания', thresholds['За 1 день до окончания'])]:
                items = OrderItem.objects.filter(kind='rental', end_date=target_date)
                for item in items:
                    subject = f'Напоминание: аренда книги «{item.book.title}» заканчивается {item.end_date}'
                    msg = (f'Здравствуйте, {item.order.user.username}!

'
                           f'Напоминаем, что аренда книги «{item.book.title}» '
                           f'заканчивается {item.end_date}. Вы можете продлить аренду или вернуть книгу.

'
                           f'— Ваш книжный магазин')
                    send_mail(subject, msg, None, [item.order.user.email or 'console@example.com'])
                    count += 1

            # Просроченные
            overdue = OrderItem.objects.filter(kind='rental', end_date__lt=today)
            for item in overdue:
                subject = f'Аренда просрочена: «{item.book.title}» (дата окончания {item.end_date})'
                msg = (f'Здравствуйте, {item.order.user.username}!

'
                       f'Срок аренды книги «{item.book.title}» истёк {item.end_date}. '
                       f'Пожалуйста, верните книгу или свяжитесь с администратором для продления.

'
                       f'— Ваш книжный магазин')
                send_mail(subject, msg, None, [item.order.user.email or 'console@example.com'])
                count += 1

            self.stdout.write(self.style.SUCCESS(f'Отправлено напоминаний: {count}'))
