from django.urls import path
from . import views

app_name = 'frontend'

urlpatterns = [
    # Mahsulotlar
    path('products/', views.products_page, name='products'),
    path('products/list/', views.product_list, name='product_list'),
    path('products/form/', views.product_form, name='product_form'),
    path('products/form/<int:pk>/', views.product_form, name='product_edit_form'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/edit/<int:pk>/', views.product_edit, name='product_edit'),
    path('products/delete/<int:pk>/', views.product_delete, name='product_delete'),

    # Buyurtmalar
    path('orders/', views.orders_page, name='orders'),
    path('orders/list/', views.order_list, name='order_list'),
    path('orders/form/', views.order_form, name='order_form'),
    path('orders/create/', views.order_create, name='order_create'),

    # Inventory – Kirimlar
    path('inventory/', views.inventory_page, name='inventory'),
    path('inventory/entries/list/', views.stock_entry_list, name='stock_entry_list'),
    path('inventory/entries/form/', views.stock_entry_form, name='stock_entry_form'),
    path('inventory/entries/create/', views.stock_entry_create, name='stock_entry_create'),
    path('inventory/entries/delete/<int:pk>/', views.stock_entry_delete, name='stock_entry_delete'),
    # Inventory – Chiqimlar
    path('inventory/exits/list/', views.stock_exit_list, name='stock_exit_list'),
    path('inventory/exits/form/', views.stock_exit_form, name='stock_exit_form'),
    path('inventory/exits/create/', views.stock_exit_create, name='stock_exit_create'),
    path('inventory/exits/delete/<int:pk>/', views.stock_exit_delete, name='stock_exit_delete'),

    # Profil
    path('profile/', views.profile, name='profile'),

    # Dashboard
    path('dashboard/', views.dashboard_page, name='dashboard'),
    path('dashboard/stats/', views.dashboard_stats, name='dashboard_stats'),
]
