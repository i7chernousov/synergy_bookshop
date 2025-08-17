from django.urls import path
from . import views

urlpatterns = [
    path('', views.BookListView.as_view(), name='book_list'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('books/<int:pk>/buy/', views.buy_book, name='buy_book'),
    path('books/<int:pk>/rent/', views.rent_book, name='rent_book'),
    path('my/orders/', views.MyOrdersView.as_view(), name='my_orders'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
