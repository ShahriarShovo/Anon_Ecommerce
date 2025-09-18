from django.urls import path
from orders.views.orders.order_views import create_order, OrderListView, OrderDetailView
from orders.views.payments.payment_views import PaymentMethodListView, mark_cod_collected, PaymentDetailView

urlpatterns = [
    # Order URLs
    path('create/', create_order, name='create_order'),
    path('', OrderListView.as_view(), name='order_list'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    
    # Payment URLs
    path('payment-methods/', PaymentMethodListView.as_view(), name='payment_method_list'),
    path('payments/<int:payment_id>/mark-cod-collected/', mark_cod_collected, name='mark_cod_collected'),
    path('payments/<int:pk>/', PaymentDetailView.as_view(), name='payment_detail'),
]
