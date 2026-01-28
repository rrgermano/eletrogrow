from django.urls import path
from .views import (
    UpcomingOutflowsAPIView,
    UpcomingMaturitiesAndTasksAPIView,
    MonthlySummaryAPIView,
    ProjectStatsAPIView,
    EarningsPeriodChartAPIView
)

app_name = 'dashboard'

urlpatterns = [
    # View original
    path('upcoming-outflows/', UpcomingOutflowsAPIView.as_view(), name='upcoming-outflows'),

    # NOVAS VIEWS
    path('upcoming/', UpcomingMaturitiesAndTasksAPIView.as_view(), name='upcoming'),
    path('summary/', MonthlySummaryAPIView.as_view(), name='summary'),
    path('project-stats/', ProjectStatsAPIView.as_view(), name='project-stats'),
    path('charts/earnings-period/', EarningsPeriodChartAPIView.as_view(), name='earnings-period-chart'),
]