from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, FileResponse
from django.template.loader import render_to_string
from django.conf import settings
import os
import tempfile
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from io import BytesIO

from invoice.models import Invoice
from invoice.serializers import InvoiceSerializer
from orders.models.orders.order import Order


class InvoiceListView(generics.ListAPIView):
    """
    List all invoices for the authenticated user
    """
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Invoice.objects.filter(order__user=self.request.user).order_by('-created_at')


class InvoiceDetailView(generics.RetrieveAPIView):
    """
    Retrieve a specific invoice
    """
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Invoice.objects.filter(order__user=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def generate_invoice(request, order_id):
    """
    Generate invoice for an order
    """
    print(f"🧾 Invoice generation: User: {request.user.email}, Order ID: {order_id}")
    
    try:
        # Get order
        order = get_object_or_404(Order, id=order_id, user=request.user)
        print(f"🧾 Order found: {order.order_number}")
        
        # Create or get invoice
        invoice, created = Invoice.objects.get_or_create(
            order=order,
            defaults={
                'status': 'sent'
            }
        )
        
        if created:
            print(f"🧾 Invoice created: {invoice.invoice_number}")
        else:
            print(f"🧾 Invoice found: {invoice.invoice_number}")
        
        # Return invoice data
        serializer = InvoiceSerializer(invoice, context={'request': request})
        
        return Response({
            'success': True,
            'message': 'Invoice generated successfully',
            'invoice': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"🧾 Invoice generation error: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'message': f'Failed to generate invoice: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def invoice_pdf_view(request, invoice_id):
    """
    Generate PDF view of invoice
    """
    try:
        invoice = get_object_or_404(Invoice, id=invoice_id, order__user=request.user)
        
        # Render invoice template
        context = {
            'invoice': invoice,
            'order': invoice.order,
            'order_items': invoice.order.items.all(),
            'delivery_address': invoice.order.delivery_address,
            'payment': invoice.order.payment,
        }
        
        html_content = render_to_string('invoice/invoice_template.html', context)
        
        return HttpResponse(html_content, content_type='text/html')
        
    except Exception as e:
        print(f"🧾 Invoice PDF error: {str(e)}")
        return Response({
            'success': False,
            'message': f'Failed to generate invoice PDF: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_invoice_pdf(request, invoice_id):
    """
    Download invoice as PDF file using ReportLab
    """
    try:
        invoice = get_object_or_404(Invoice, id=invoice_id, order__user=request.user)
        print(f"🧾 PDF Download: Invoice {invoice.invoice_number}")
        
        # Create BytesIO buffer for PDF
        buffer = BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#28a745')
        )
        
        header_style = ParagraphStyle(
            'Header',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor('#28a745')
        )
        
        normal_style = ParagraphStyle(
            'Normal',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6
        )
        
        # Build PDF content
        story = []
        
        # Title
        story.append(Paragraph("🛍️ INVOICE", title_style))
        story.append(Spacer(1, 20))
        
        # Invoice details
        story.append(Paragraph(f"<b>Invoice Number:</b> {invoice.invoice_number}", normal_style))
        story.append(Paragraph(f"<b>Invoice Date:</b> {invoice.get_invoice_date_display()}", normal_style))
        story.append(Paragraph(f"<b>Due Date:</b> {invoice.get_due_date_display()}", normal_style))
        story.append(Spacer(1, 20))
        
        # Company info
        story.append(Paragraph("🛍️ " + (invoice.company_name or "Anon Ecommerce"), header_style))
        story.append(Paragraph(f"<b>Email:</b> {invoice.company_email or 'info@anonecommerce.com'}", normal_style))
        story.append(Paragraph(f"<b>Phone:</b> {invoice.company_phone or '+880 1234 567890'}", normal_style))
        story.append(Paragraph(f"<b>Address:</b> {invoice.company_address or 'Dhaka, Bangladesh'}", normal_style))
        story.append(Spacer(1, 20))
        
        # Customer info
        story.append(Paragraph("Bill To:", header_style))
        story.append(Paragraph(f"<b>Name:</b> {invoice.order.delivery_address.full_name}", normal_style))
        story.append(Paragraph(f"<b>Phone:</b> {invoice.order.delivery_address.phone_number}", normal_style))
        story.append(Paragraph(f"<b>Address:</b> {invoice.order.delivery_address.address_line_1}", normal_style))
        story.append(Paragraph(f"<b>City:</b> {invoice.order.delivery_address.city}", normal_style))
        story.append(Paragraph(f"<b>Country:</b> {invoice.order.delivery_address.country}", normal_style))
        story.append(Spacer(1, 20))
        
        # Order items table
        story.append(Paragraph("Order Items:", header_style))
        
        # Table data
        table_data = [['Product', 'SKU', 'Quantity', 'Unit Price', 'Total']]
        
        for item in invoice.order.items.all():
            table_data.append([
                item.product_name or 'N/A',
                item.product_sku or 'N/A',
                str(item.quantity),
                f"৳{item.unit_price:,.2f}",
                f"৳{item.total_price:,.2f}"
            ])
        
        # Create table
        table = Table(table_data, colWidths=[2*inch, 1*inch, 0.8*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#28a745')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        # Totals
        story.append(Paragraph("Order Summary:", header_style))
        story.append(Paragraph(f"<b>Subtotal:</b> ৳{invoice.order.subtotal:,.2f}", normal_style))
        story.append(Paragraph(f"<b>Shipping Cost:</b> ৳{invoice.get_shipping_cost():,.2f}", normal_style))
        story.append(Paragraph(f"<b>Tax Amount:</b> ৳{invoice.get_tax_amount():,.2f}", normal_style))
        story.append(Paragraph(f"<b>Total Amount:</b> ৳{invoice.order.total_amount:,.2f}", normal_style))
        story.append(Spacer(1, 20))
        
        # Payment info
        if invoice.order.payment:
            story.append(Paragraph("Payment Information:", header_style))
            story.append(Paragraph(f"<b>Payment Method:</b> {invoice.order.payment.payment_method.name if invoice.order.payment.payment_method else 'N/A'}", normal_style))
            story.append(Paragraph(f"<b>Status:</b> {invoice.order.payment.status}", normal_style))
            if invoice.order.payment.payment_method and invoice.order.payment.payment_method.is_cod:
                story.append(Paragraph("<i>This is a Cash on Delivery order. Payment will be collected upon delivery.</i>", normal_style))
        
        # Notes
        if invoice.order.notes:
            story.append(Spacer(1, 20))
            story.append(Paragraph("Notes:", header_style))
            story.append(Paragraph(invoice.order.notes, normal_style))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF content
        pdf_content = buffer.getvalue()
        buffer.close()
        
        # Create response
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
        response['Content-Length'] = len(pdf_content)
        
        print(f"🧾 PDF generated successfully: {len(pdf_content)} bytes")
        return response
        
    except Exception as e:
        print(f"🧾 PDF download error: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'message': f'Failed to download invoice PDF: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
