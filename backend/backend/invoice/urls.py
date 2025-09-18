from django.urls import path
from invoice.views import InvoiceListView, InvoiceDetailView, generate_invoice, invoice_pdf_view, download_invoice_pdf

urlpatterns = [
    # Invoice URLs
    path('', InvoiceListView.as_view(), name='invoice_list'),
    path('<int:pk>/', InvoiceDetailView.as_view(), name='invoice_detail'),
    path('generate/<int:order_id>/', generate_invoice, name='generate_invoice'),
    path('<int:invoice_id>/pdf/', invoice_pdf_view, name='invoice_pdf'),
    path('<int:invoice_id>/download/', download_invoice_pdf, name='download_invoice_pdf'),
]
