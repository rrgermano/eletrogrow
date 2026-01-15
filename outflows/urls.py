from django.urls import path, include
from .views import (ListOutflow,
                    CreateOutflow,
                    UpdateOutflow,
                    DetailOutflow,
                    DeleteOutflow,
                    DetailCreditOutflow,
                    ListCreditOutflow,
                    UpdateCreditOutflow,
                    DeleteCreditOutflow,
                    CreateOutflowTypeChoice,
                    UpdateOutflowTypeChoice,
                    DeleteOutflowTypeChoice,
                    favored_autocomplete,
                    project_autocomplete
                    )

urlpatterns = [
    path('', ListOutflow.as_view(), name='outflow'),
    path('credit/', ListCreditOutflow.as_view(), name='outflow_credit'),
    path('new/', CreateOutflow.as_view(), name='new_outflow'),
    path('update/<int:pk>/', UpdateOutflow.as_view(), name='update_outflow'),
    path('credit/update/<int:pk>/', UpdateCreditOutflow.as_view(), name='update_credit_outflow'),
    path('detail/<int:pk>/', DetailOutflow.as_view(), name='detail_outflow'),
    path('credit/detail/<int:pk>/', DetailCreditOutflow.as_view(), name='detail_credit_outflow'),
    path('delete/<int:pk>/', DeleteOutflow.as_view(), name='delete_outflow'),
    path('credit/delete/<int:pk>/', DeleteCreditOutflow.as_view(), name='delete_credit_outflow'),
    path('choices/new/', CreateOutflowTypeChoice.as_view(), name='new_outflow_choice'),
    path('choices/update/<int:pk>/', UpdateOutflowTypeChoice.as_view(), name='update_outflow_choice'),
    path('choices/delete/<int:pk>/', DeleteOutflowTypeChoice.as_view(), name='delete_outflow_choice'),
    path('favored-autocomplete/', favored_autocomplete, name='favored-autocomplete'),
    path('project-autocomplete/', project_autocomplete, name='project-autocomplete'),

]