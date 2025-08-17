from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import Author, Category, Book

class Command(BaseCommand):
    help = 'Создаёт демо-данные: пользователей, авторов, категории, книги.'

    def handle(self, *args, **kwargs):
        # users
        for username in ['admin', 'ivan', 'olga']:
            user, created = User.objects.get_or_create(username=username, defaults={'email': f'{username}@example.com'})
            if created or not user.has_usable_password():
                user.set_password('password')
                user.save()
        admin = User.objects.get(username='admin')
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()

        # authors
        a1, _ = Author.objects.get_or_create(name='Джордж Оруэлл')
        a2, _ = Author.objects.get_or_create(name='Рей Брэдбери')
        a3, _ = Author.objects.get_or_create(name='Лев Толстой')

        # categories
        from django.utils.text import slugify
        c1, _ = Category.objects.get_or_create(name='Антиутопия', defaults={'slug': slugify('Антиутопия')})
        c2, _ = Category.objects.get_or_create(name='Классика', defaults={'slug': slugify('Классика')})
        c3, _ = Category.objects.get_or_create(name='Фантастика', defaults={'slug': slugify('Фантастика')})

        # books
        Book.objects.get_or_create(title='1984', author=a1, category=c1, year=1949,
                                   defaults={'description': 'Культовая антиутопия.', 'available_copies': 3,
                                             'price_purchase': 14.99, 'price_rent_2w': 3.99, 'price_rent_1m': 5.99, 'price_rent_3m': 9.99})
        Book.objects.get_or_create(title='Скотный двор', author=a1, category=c1, year=1945,
                                   defaults={'description': 'Сатирическая повесть-притча.', 'available_copies': 2,
                                             'price_purchase': 12.99, 'price_rent_2w': 2.99, 'price_rent_1m': 4.99, 'price_rent_3m': 7.99})
        Book.objects.get_or_create(title='451° по Фаренгейту', author=a2, category=c3, year=1953,
                                   defaults={'description': 'О запрете книг и власти экранов.', 'available_copies': 4,
                                             'price_purchase': 13.99, 'price_rent_2w': 3.49, 'price_rent_1m': 5.49, 'price_rent_3m': 8.99})
        Book.objects.get_or_create(title='Война и мир', author=a3, category=c2, year=1869,
                                   defaults={'description': 'Эпопея о людях и истории.', 'available_copies': 1,
                                             'price_purchase': 19.99, 'price_rent_2w': 4.99, 'price_rent_1m': 6.99, 'price_rent_3m': 10.99})

        self.stdout.write(self.style.SUCCESS('Демо-данные созданы. Логин админки: admin/password'))
