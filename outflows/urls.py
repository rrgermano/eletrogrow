from django.urls import path
from .views import (ListOutflow,
                    CreateOutflow,
                    #UpdateInflow,
                    #DetailInflow,
                    #DeleteInflow,
                    )

urlpatterns = [
    path('', ListOutflow.as_view(), name='outflow'),
    path('new/', CreateOutflow.as_view(), name='new_outflow'),
#    path('update/<int:pk>/', UpdateInflow.as_view(), name='update_outflow'),
#    path('detail/<int:pk>', DetailInflow.as_view(), name='detail_outflow'),
#    path('delete/<int:pk>', DeleteInflow.as_view(), name='delete_outflow'),
]