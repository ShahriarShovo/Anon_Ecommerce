from django.urls import path
from orders.views.orders.order_views import create_order, OrderListView, ActiveOrderListView, OrderDetailView, DeliveredOrderListView, CancelledRefundedOrderListView, update_order_status, cancel_order
from orders.views.payments.payment_views import PaymentMethodListView, mark_cod_collected, PaymentDetailView
from orders.views.orders.address_views import AddressListView, AddressDetailView, set_default_address, get_default_address

urlpatterns = [
    # Order URLs
    path('create/', create_order, name='create_order'),
    path('', OrderListView.as_view(), name='order_list'),
    path('active/', ActiveOrderListView.as_view(), name='active_order_list'),
    path('delivered/', DeliveredOrderListView.as_view(), name='delivered_order_list'),
    path('cancelled-refunded/', CancelledRefundedOrderListView.as_view(), name='cancelled_refunded_order_list'),
    path('<int:order_id>/update-status/', update_order_status, name='update_order_status'),
    path('<int:order_id>/cancel/', cancel_order, name='cancel_order'), # New cancel order endpoint
    path('<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    
    # Payment URLs
    path('payment-methods/', PaymentMethodListView.as_view(), name='payment_method_list'),
    path('payments/<int:payment_id>/mark-cod-collected/', mark_cod_collected, name='mark_cod_collected'),
    path('payments/<int:pk>/', PaymentDetailView.as_view(), name='payment_detail'),
    
    # Address URLs
    path('addresses/', AddressListView.as_view(), name='address_list'),
    path('addresses/<int:pk>/', AddressDetailView.as_view(), name='address_detail'),
    path('addresses/<int:address_id>/set-default/', set_default_address, name='set_default_address'),
    path('addresses/default/', get_default_address, name='get_default_address'),
]
