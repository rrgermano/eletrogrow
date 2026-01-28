from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView, TokenVerifyView

urlpatterns =[
    path('services/', include('services.urls_api')),
    path('projects/', include('projects.urls_api')),
    path('clients/', include('clients.urls_api')),
    path('inflows/', include('inflows.urls_api')),
    path('suppliers/', include('supplier.urls_api')),
    path('outflows/', include('outflows.urls_api')),
    path('dashboard/', include('dashboard.urls_api')),
    path('token/', TokenObtainPairView.as_view(), name='obtain-token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='refresh-token'),
    path('token/verify/', TokenVerifyView.as_view(), name='verify-token')
]