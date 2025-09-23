from django.urls import path
from analytics import views

urlpatterns = [
    path('sales-analytics/', views.sales_analytics, name='sales_analytics'),
    path('sales-trends/', views.sales_trends, name='sales_trends'),
    path('excel-report/', views.generate_excel_report, name='excel_report'),
]
