from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone

User = settings.AUTH_USER_MODEL

class Author(models.Model):
    name = models.CharField(max_length=120)
    bio = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Book(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = 'available', 'Доступна'
        OUT_OF_STOCK = 'out', 'Нет в наличии'
        ARCHIVED = 'archived', 'Снята с продажи'

    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='books')
    year = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.AVAILABLE)
    available_copies = models.PositiveIntegerField(default=1)
    price_purchase = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    price_rent_2w = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    price_rent_1m = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    price_rent_3m = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    cover_url = models.URLField(blank=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f"{self.title} — {self.author}"

    def get_absolute_url(self):
        return reverse('book_detail', args=[self.pk])

    @property
    def active_rentals_count(self):
        return self.order_items.filter(kind=OrderItem.Kind.RENTAL, end_date__gte=timezone.now().date()).count()

    @property
    def units_available_now(self):
        # Доступно = базовое количество минус активные аренды
        return max(0, self.available_copies - self.active_rentals_count)

    def can_be_purchased(self):
        return self.status == Book.Status.AVAILABLE and self.units_available_now > 0

    def can_be_rented(self):
        return self.status == Book.Status.AVAILABLE and self.units_available_now > 0

class Order(models.Model):
    class Status(models.TextChoices):
        CREATED = 'created', 'Создан'
        COMPLETED = 'completed', 'Завершён'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.COMPLETED)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ #{self.pk} от {self.user}"

class OrderItem(models.Model):
    class Kind(models.TextChoices):
        PURCHASE = 'purchase', 'Покупка'
        RENTAL = 'rental', 'Аренда'

    class Duration(models.TextChoices):
        TWO_WEEKS = '2w', '2 недели'
        ONE_MONTH = '1m', '1 месяц'
        THREE_MONTHS = '3m', '3 месяца'

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name='order_items')
    kind = models.CharField(max_length=10, choices=Kind.choices)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    duration = models.CharField(max_length=2, choices=Duration.choices, blank=True)

    def __str__(self):
        return f"{self.get_kind_display()} — {self.book.title}"

    def is_active_rental(self):
        if self.kind != OrderItem.Kind.RENTAL or not self.end_date:
            return False
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date
