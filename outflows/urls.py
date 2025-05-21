from django.urls import path
from .views import (ListOutflow,
                    CreateOutflow,
                    UpdateOutflow,
                    DetailOutflow,
                    DeleteOutflow,
                    )

urlpatterns = [
    path('', ListOutflow.as_view(), name='outflow'),
    path('new/', CreateOutflow.as_view(), name='new_outflow'),
    path('update/<int:pk>/', UpdateOutflow.as_view(), name='update_outflow'),
    path('detail/<int:pk>', DetailOutflow.as_view(), name='detail_outflow'),
    path('delete/<int:pk>', DeleteOutflow.as_view(), name='delete_outflow'),
]