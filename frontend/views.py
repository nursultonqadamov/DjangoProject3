from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.template.context_processors import csrf
from django.db.models import Sum, Count
from datetime import datetime, timedelta

from products.models import Product
from orders.models import Order, OrderItem
from inventory.models import StockEntry, StockExit, CurrentStock
from customers.models import CustomerProfile
from decimal import Decimal

User = get_user_model()

@login_required
def products_page(request):
    return render(request, 'frontend/products.html')

@login_required
def product_list(request):
    products = Product.objects.all().order_by('-created_at')
    context = {'products': products}
    context.update(csrf(request))
    html = render_to_string('frontend/_product_list.html', context, request=request)
    return HttpResponse(html)

@login_required
def product_form(request, pk=None):
    if pk:
        product = get_object_or_404(Product, id=pk)
    else:
        product = None
    
    context = {
        'product': product,
    }
    context.update(csrf(request))
    html = render_to_string('frontend/_product_form.html', context, request=request)
    return HttpResponse(html)

@login_required
@require_http_methods(["POST"])
def product_create(request):
    name = request.POST.get('name')
    price = request.POST.get('price')
    category = request.POST.get('category')
    stock = request.POST.get('stock')
    description = request.POST.get('description', '')
    image = request.FILES.get('image', None)

    if not all([name, price, category, stock]):
        return HttpResponseBadRequest("Barcha kerakli maydonlarni to'ldiring.")

    try:
        price = Decimal(price)
        stock = int(stock)
    except (ValueError, TypeError):
        return HttpResponseBadRequest("Narx yoki zaxira noto'g'ri formatda.")

    p = Product.objects.create(
        name=name,
        price=price,
        category=category,
        stock=stock,
        description=description,
        image=image
    )
    
    # CurrentStock yangilash
    CurrentStock.objects.get_or_create(product=p, defaults={'quantity': stock})

    # Ro'yxatni yangilaymiz
    products = Product.objects.all().order_by('-created_at')
    context = {'products': products}
    context.update(csrf(request))
    html = render_to_string('frontend/_product_list.html', context, request=request)
    return HttpResponse(html)

@login_required
@require_http_methods(["POST"])
def product_edit(request, pk):
    product = get_object_or_404(Product, id=pk)
    name = request.POST.get('name')
    price = request.POST.get('price')
    category = request.POST.get('category')
    stock = request.POST.get('stock')
    description = request.POST.get('description', '')
    image = request.FILES.get('image', None)

    if not all([name, price, category, stock]):
        return HttpResponseBadRequest("Barcha kerakli maydonlarni to'ldiring.")

    try:
        price = Decimal(price)
        stock = int(stock)
    except (ValueError, TypeError):
        return HttpResponseBadRequest("Narx yoki zaxira noto'g'ri formatda.")

    product.name = name
    product.price = price
    product.category = category
    product.stock = stock
    product.description = description
    if image:
        product.image = image
    product.save()

    # CurrentStock yangilash
    cs, created = CurrentStock.objects.get_or_create(product=product)
    cs.quantity = stock
    cs.save()

    products = Product.objects.all().order_by('-created_at')
    context = {'products': products}
    context.update(csrf(request))
    html = render_to_string('frontend/_product_list.html', context, request=request)
    return HttpResponse(html)

@login_required
@require_http_methods(["DELETE"])
def product_delete(request, pk):
    product = get_object_or_404(Product, id=pk)
    product.delete()
    products = Product.objects.all().order_by('-created_at')
    context = {'products': products}
    context.update(csrf(request))
    html = render_to_string('frontend/_product_list.html', context, request=request)
    return HttpResponse(html)

@login_required
def orders_page(request):
    return render(request, 'frontend/orders.html')

@login_required
def order_list(request):
    if request.user.is_staff:
        orders = Order.objects.all().order_by('-created_at')
    else:
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
    html = render_to_string('frontend/_order_list.html', {'orders': orders}, request=request)
    return HttpResponse(html)

@login_required
def order_form(request):
    products = Product.objects.filter(stock__gt=0)
    html = render_to_string('frontend/_order_form.html', {
        'products': products,
        'order': Order,
    }, request=request)
    return HttpResponse(html)

@login_required
@require_http_methods(["POST"])
def order_create(request):
    product_id = request.POST.get('product_id')
    quantity = request.POST.get('quantity')
    status = request.POST.get('status')

    try:
        quantity = int(quantity)
        product = Product.objects.get(id=product_id)
    except:
        return HttpResponseBadRequest("Mahsulot yoki miqdor noto'g'ri.")

    if product.stock < quantity:
        return HttpResponseBadRequest("Tovar zaxirasida yetarli miqdor yo'q.")

    order = Order.objects.create(
        user=request.user,
        status=status,
        total_price=product.price * quantity
    )
    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=quantity
    )
    
    product.stock -= quantity
    product.save()
    cs = CurrentStock.objects.get(product=product)
    cs.quantity -= quantity
    cs.save()

    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    html = render_to_string('frontend/_order_list.html', {'orders': orders}, request=request)
    return HttpResponse(html)

@login_required
def inventory_page(request):
    return render(request, 'frontend/inventory.html')

@login_required
def stock_entry_list(request):
    entries = StockEntry.objects.all().order_by('-timestamp')
    context = {'entries': entries}
    context.update(csrf(request))
    html = render_to_string('frontend/_stock_entry_list.html', context, request=request)
    return HttpResponse(html)

@login_required
def stock_entry_form(request):
    products = Product.objects.all()
    context = {'products': products}
    context.update(csrf(request))
    html = render_to_string('frontend/_stock_entry_form.html', context, request=request)
    return HttpResponse(html)

@login_required
@require_http_methods(["POST"])
def stock_entry_create(request):
    product_id = request.POST.get('product_id')
    quantity = request.POST.get('quantity')
    note = request.POST.get('note', '')

    if not all([product_id, quantity]):
        return HttpResponseBadRequest("Mahsulot va miqdorni tanlang.")

    try:
        quantity = int(quantity)
        product = Product.objects.get(id=product_id)
    except (ValueError, TypeError, Product.DoesNotExist):
        return HttpResponseBadRequest("Mahsulot yoki miqdor noto'g'ri.")

    entry = StockEntry.objects.create(
        product=product,
        quantity=quantity,
        entered_by=request.user,
        note=note
    )
    
    # Product stock yangilash
    product.stock += quantity
    product.save()
    
    # CurrentStock yangilash
    cs, created = CurrentStock.objects.get_or_create(product=product)
    cs.quantity += quantity
    cs.save()

    entries = StockEntry.objects.all().order_by('-timestamp')
    context = {'entries': entries}
    context.update(csrf(request))
    html = render_to_string('frontend/_stock_entry_list.html', context, request=request)
    return HttpResponse(html)

@login_required
@require_http_methods(["DELETE"])
def stock_entry_delete(request, pk):
    entry = get_object_or_404(StockEntry, id=pk)
    product = entry.product
    product.stock -= entry.quantity
    product.save()
    cs = CurrentStock.objects.get(product=product)
    cs.quantity -= entry.quantity
    cs.save()
    entry.delete()

    entries = StockEntry.objects.all().order_by('-timestamp')
    context = {'entries': entries}
    context.update(csrf(request))
    html = render_to_string('frontend/_stock_entry_list.html', context, request=request)
    return HttpResponse(html)

@login_required
def stock_exit_list(request):
    exits = StockExit.objects.all().order_by('-timestamp')
    context = {'exits': exits}
    context.update(csrf(request))
    html = render_to_string('frontend/_stock_exit_list.html', context, request=request)
    return HttpResponse(html)

@login_required
def stock_exit_form(request):
    products = Product.objects.filter(stock__gt=0)
    context = {'products': products}
    context.update(csrf(request))
    html = render_to_string('frontend/_stock_exit_form.html', context, request=request)
    return HttpResponse(html)

@login_required
@require_http_methods(["POST"])
def stock_exit_create(request):
    product_id = request.POST.get('product_id')
    quantity = request.POST.get('quantity')
    note = request.POST.get('note', '')

    if not all([product_id, quantity]):
        return HttpResponseBadRequest("Mahsulot va miqdorni tanlang.")

    try:
        quantity = int(quantity)
        product = Product.objects.get(id=product_id)
    except (ValueError, TypeError, Product.DoesNotExist):
        return HttpResponseBadRequest("Mahsulot yoki miqdor noto'g'ri.")

    if product.stock < quantity:
        return HttpResponseBadRequest("Zaxira yetarli emas.")

    exit = StockExit.objects.create(
        product=product,
        quantity=quantity,
        removed_by=request.user,
        note=note
    )
    
    # CurrentStock yangilash
    cs = CurrentStock.objects.get(product=product)
    cs.quantity -= quantity
    cs.save()
    product.stock -= quantity
    product.save()

    exits = StockExit.objects.all().order_by('-timestamp')
    context = {'exits': exits}
    context.update(csrf(request))
    html = render_to_string('frontend/_stock_exit_list.html', context, request=request)
    return HttpResponse(html)

@login_required
@require_http_methods(["DELETE"])
def stock_exit_delete(request, pk):
    exit = get_object_or_404(StockExit, id=pk)
    product = exit.product
    product.stock += exit.quantity
    product.save()
    cs = CurrentStock.objects.get(product=product)
    cs.quantity += exit.quantity
    cs.save()
    exit.delete()

    exits = StockExit.objects.all().order_by('-timestamp')
    context = {'exits': exits}
    context.update(csrf(request))
    html = render_to_string('frontend/_stock_exit_list.html', context, request=request)
    return HttpResponse(html)

@login_required
def profile(request):
    user = request.user
    profile, created = CustomerProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        username = request.POST.get('username')
        phone = request.POST.get('phone')
        address = request.POST.get('address', '')
        city = request.POST.get('city', '')
        country = request.POST.get('country', '')

        user.username = username
        user.save()

        profile.phone = phone
        profile.address = address
        profile.city = city
        profile.country = country
        profile.save()

        return HttpResponse("<div class='p-2 bg-green-100 text-green-800 rounded'>Profil saqlandi</div>")

    context = {
        'user': user,
        'profile': profile
    }
    return render(request, 'frontend/profile.html', context)

@login_required
def dashboard_page(request):
    return render(request, 'frontend/dashboard.html')

@login_required
def dashboard_stats(request):
    # To'g'ridan-to'g'ri ma'lumotlar bazasidan ma'lumot olish
    try:
        # Asosiy statistikalar
        total_users = User.objects.count()
        total_products = Product.objects.count()
        
        # Orders jadvalidan ma'lumotlar
        total_orders = Order.objects.count()
        total_revenue = Order.objects.aggregate(
            revenue=Sum('total_price')
        )['revenue'] or 0

        # Inventory ma'lumotlari
        total_stock_entries = StockEntry.objects.count()
        total_stock_exits = StockExit.objects.count()
        
        # Jami zaxira
        total_stock = Product.objects.aggregate(
            total=Sum('stock')
        )['total'] or 0

        # Kam zaxirali mahsulotlar
        low_stock_products = Product.objects.filter(stock__lt=10).count()

        # Bugungi operatsiyalar
        today = datetime.now().date()
        today_entries = StockEntry.objects.filter(timestamp__date=today).count()
        today_exits = StockExit.objects.filter(timestamp__date=today).count()
        today_operations = today_entries + today_exits

        # Eng ko'p zaxirali mahsulotlar
        top_stock_products = Product.objects.filter(stock__gt=0).order_by('-stock')[:5]
        
        # Eng ko'p sotilgan mahsulotlar
        top_products = []
        if OrderItem.objects.exists():
            top_products = (
                OrderItem.objects
                .values('product__name')
                .annotate(total_ordered=Sum('quantity'))
                .order_by('-total_ordered')[:5]
            )

        # Ma'lumotlarni tayyorlash
        stats = {
            'total_users': total_users,
            'total_orders': total_orders,
            'total_products': total_products,
            'total_revenue': float(total_revenue),
            'total_stock': total_stock,
            'low_stock_products': low_stock_products,
            'today_orders': today_operations,
            'total_stock_entries': total_stock_entries,
            'total_stock_exits': total_stock_exits,
            'top_products': list(top_products),
            'top_stock_products': [
                {'name': p.name, 'stock': p.stock} 
                for p in top_stock_products
            ],
        }

        html = render_to_string('frontend/_dashboard_stats.html', {'stats': stats}, request=request)
        return HttpResponse(html)
        
    except Exception as e:
        # Xatolik bo'lsa, bo'sh ma'lumotlar qaytarish
        stats = {
            'total_users': 0,
            'total_orders': 0,
            'total_products': 0,
            'total_revenue': 0,
            'total_stock': 0,
            'low_stock_products': 0,
            'today_orders': 0,
            'total_stock_entries': 0,
            'total_stock_exits': 0,
            'top_products': [],
            'top_stock_products': [],
        }
        html = render_to_string('frontend/_dashboard_stats.html', {'stats': stats}, request=request)
        return HttpResponse(html)
