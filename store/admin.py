from django.contrib import admin
from .models import Author, Category, Book, Order, OrderItem

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'year', 'status', 'available_copies', 'price_purchase')
    list_filter = ('status', 'category', 'author', 'year')
    search_fields = ('title', 'author__name')
    list_editable = ('status', 'available_copies', 'price_purchase')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('book', 'kind', 'price', 'start_date', 'end_date', 'duration')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'status', 'total')
    list_filter = ('status', 'created_at')
    inlines = [OrderItemInline]
