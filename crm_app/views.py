from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from products.models import Product
from orders.models import Order, OrderItem
from inventory.models import StockEntry, StockExit
from django.db.models import Sum, Count
from datetime import datetime, timedelta
from django.db.models.functions import TruncMonth
# Create your views here.


User = get_user_model()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    # Asosiy statistikalar
    total_users = User.objects.count()
    total_products = Product.objects.count()
    
    # Orders jadvalidan ma'lumotlar (agar mavjud bo'lsa)
    total_orders = Order.objects.count() if Order.objects.exists() else 0
    total_revenue = Order.objects.aggregate(
        revenue=Sum('total_price')
    )['revenue'] or 0

    # Inventory ma'lumotlari
    total_stock_entries = StockEntry.objects.count()
    total_stock_exits = StockExit.objects.count()
    
    # Jami zaxira (Product jadvalidan)
    total_stock = Product.objects.aggregate(
        total=Sum('stock')
    )['total'] or 0

    # Kam zaxirali mahsulotlar (10 dan kam)
    low_stock_products = Product.objects.filter(stock__lt=10).count()

    # Bugungi inventory operatsiyalari
    today = datetime.now().date()
    today_entries = StockEntry.objects.filter(created_at__date=today).count()
    today_exits = StockExit.objects.filter(created_at__date=today).count()
    today_operations = today_entries + today_exits

    # Eng ko'p zaxirali mahsulotlar (Order bo'lmasa)
    top_stock_products = Product.objects.filter(stock__gt=0).order_by('-stock')[:5]
    
    # Eng ko'p sotilgan mahsulotlar (agar Order mavjud bo'lsa)
    top_products = []
    if Order.objects.exists() and OrderItem.objects.exists():
        top_products = (
            OrderItem.objects
            .values('product__name')
            .annotate(total_ordered=Sum('quantity'))
            .order_by('-total_ordered')[:5]
        )

    # Oxirgi 6 oylik sotuvlar (agar mavjud bo'lsa)
    monthly_sales = []
    if Order.objects.exists():
        last_6_months = datetime.now() - timedelta(days=180)
        monthly_sales = (
            Order.objects.filter(created_at__gte=last_6_months)
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(total=Sum('total_price'))
            .order_by('month')
        )

    return Response({
        'total_users': total_users,
        'total_orders': total_orders,
        'total_products': total_products,
        'total_revenue': float(total_revenue),
        'total_stock': total_stock,
        'low_stock_products': low_stock_products,
        'today_orders': today_operations,  # Bugungi operatsiyalar
        'total_stock_entries': total_stock_entries,
        'total_stock_exits': total_stock_exits,
        'top_products': list(top_products),
        'top_stock_products': [
            {'name': p.name, 'stock': p.stock} 
            for p in top_stock_products
        ],
        'monthly_sales': list(monthly_sales),
    })
