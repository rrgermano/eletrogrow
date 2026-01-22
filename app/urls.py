from django.contrib import admin
from django.contrib.auth import views as auth_view
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import root_redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', root_redirect, name='root'),
    path('login/', auth_view.LoginView.as_view(), name='login'),
    path('logout/', auth_view.LogoutView.as_view(), name='logout'),
    path('client/', include('clients.urls')),
    path('project/', include('projects.urls')),
    path('inflow/', include('inflows.urls')),
    path('outflow/', include('outflows.urls')),
    path('supplier/', include('supplier.urls')),
    path('api/v1/', include('app.urls_api')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
