from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views

# Boshlang'ichni login sahifasiga yo'naltiruvchi funktsiya
def index_redirect(request):
    if request.user.is_authenticated:
        return redirect('frontend:dashboard')
    return redirect('login')

urlpatterns = [
    # "/" ga kirganda index_redirect ishlaydi
    path('', index_redirect),

    path('admin/', admin.site.urls),

    # API endpoint'lar (oldin o'rnatilganlar)
    path('api/accounts/', include('accounts.urls')),
    path('api/products/', include('products.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/customers/', include('customers.urls')),
    path('api/inventory/', include('inventory.urls')),
    path('api/dashboard/', include('crm_app.urls')),

    # Django auth (login & logout)
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    
    # Logout - GET va POST lar uchun
    path('logout/', auth_views.LogoutView.as_view(
        next_page='login',
        http_method_names=['get', 'post']
    ), name='logout'),

    # HTMX frontend
    path('', include('frontend.urls', namespace='frontend')),
]
