from django.urls import path, include

urlpatterns =[
    path('services/', include('services.urls_api')),
    path('projects/', include('projects.urls_api')),
    path('clients/', include('clients.urls_api')),
    path('inflows/', include('inflows.urls_api')),
]