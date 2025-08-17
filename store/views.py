from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import ListView

from .forms import RentalForm
from .models import Author, Book, Category, Order, OrderItem

class BookListView(ListView):
    template_name = 'store/book_list.html'
    context_object_name = 'books'
    paginate_by = 12

    def get_queryset(self):
        qs = Book.objects.all().select_related('author', 'category')
        # фильтры
        category = self.request.GET.get('category')
        author = self.request.GET.get('author')
        year = self.request.GET.get('year')
        if category:
            qs = qs.filter(category__slug=category)
        if author:
            qs = qs.filter(author__id=author)
        if year:
            qs = qs.filter(year=year)
        # сортировка
        sort = self.request.GET.get('sort')
        if sort == 'category':
            qs = qs.order_by('category__name', 'title')
        elif sort == 'author':
            qs = qs.order_by('author__name', 'title')
        elif sort == 'year':
            qs = qs.order_by('year', 'title')
        else:
            qs = qs.order_by('title')
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Category.objects.all()
        ctx['authors'] = Author.objects.all()
        ctx['active_filters'] = {
            'category': self.request.GET.get('category', ''),
            'author': self.request.GET.get('author', ''),
            'year': self.request.GET.get('year', ''),
            'sort': self.request.GET.get('sort', ''),
        }
        return ctx

def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    rental_form = RentalForm()
    return render(request, 'store/book_detail.html', {'book': book, 'rental_form': rental_form})

@login_required
def buy_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if not book.can_be_purchased():
        messages.error(request, 'Книга недоступна для покупки.')
        return redirect(book.get_absolute_url())
    order = Order.objects.create(user=request.user, total=book.price_purchase)
    OrderItem.objects.create(order=order, book=book, kind=OrderItem.Kind.PURCHASE, price=book.price_purchase)
    # уменьшаем доступные экземпляры
    if book.available_copies > 0:
        book.available_copies -= 1
        book.save(update_fields=['available_copies'])
    messages.success(request, f'Книга «{book.title}» куплена. Заказ #{order.pk}')
    return redirect('my_orders')

@login_required
def rent_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if not book.can_be_rented():
        messages.error(request, 'Книга недоступна для аренды.')
        return redirect(book.get_absolute_url())
    if request.method == 'POST':
        form = RentalForm(request.POST)
        if form.is_valid():
            duration = form.cleaned_data['duration']
            days = {'2w': 14, '1m': 30, '3m': 90}[duration]
            start = timezone.now().date()
            end = start + timedelta(days=days)
            price_map = {
                '2w': book.price_rent_2w,
                '1m': book.price_rent_1m,
                '3m': book.price_rent_3m,
            }
            price = Decimal(price_map[duration])
            order = Order.objects.create(user=request.user, total=price)
            OrderItem.objects.create(
                order=order,
                book=book,
                kind=OrderItem.Kind.RENTAL,
                price=price,
                start_date=start,
                end_date=end,
                duration=duration
            )
            messages.success(request, f'Вы арендовали «{book.title}» до {end.strftime("%d.%m.%Y")} (заказ #{order.pk}).')
            return redirect('my_orders')
    else:
        form = RentalForm()
    return render(request, 'store/rent_book.html', {'book': book, 'form': form})

class MyOrdersView(LoginRequiredMixin, ListView):
    template_name = 'store/my_orders.html'
    context_object_name = 'orders'
    paginate_by = 20

    def get_queryset(self):
        return (Order.objects
                .filter(user=self.request.user)
                .prefetch_related('items__book', 'items'))

@staff_member_required
def dashboard(request):
    # простая админ-панель: ближайшие возвраты и книги с малым остатком
    upcoming = OrderItem.objects.filter(kind=OrderItem.Kind.RENTAL, end_date__gte=timezone.now().date()).order_by('end_date')[:20]
    low_stock = Book.objects.filter(status=Book.Status.AVAILABLE, available_copies__lte=1).order_by('available_copies')[:20]
    return render(request, 'store/dashboard.html', {'upcoming': upcoming, 'low_stock': low_stock})
