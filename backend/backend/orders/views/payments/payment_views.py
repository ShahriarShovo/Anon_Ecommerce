from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from orders.models.payments.payment import Payment
from orders.models.payments.payment_method import PaymentMethod
from orders.serializers.payments.payment_serializer import PaymentSerializer, PaymentMethodSerializer


class PaymentMethodListView(generics.ListAPIView):
    """
    List all active payment methods
    """
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.AllowAny]  # Allow anonymous access for payment methods
    
    def get_queryset(self):
        return PaymentMethod.objects.filter(is_active=True).order_by('display_order', 'name')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_cod_collected(request, payment_id):
    """
    Mark cash on delivery payment as collected
    """
    try:
        payment = get_object_or_404(Payment, id=payment_id, order__user=request.user)
        
        if not payment.is_cash_on_delivery():
            return Response({
                'success': False,
                'message': 'This is not a cash on delivery payment'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if payment.cod_collected:
            return Response({
                'success': False,
                'message': 'Payment already marked as collected'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Mark as collected
        payment.cod_collected = True
        payment.cod_collected_by = request.data.get('collected_by', request.user.email)
        payment.status = 'completed'
        payment.save()
        
        # Update order status to confirmed
        payment.order.status = 'confirmed'
        payment.order.save()
        
        serializer = PaymentSerializer(payment, context={'request': request})
        
        return Response({
            'success': True,
            'message': 'Payment marked as collected successfully',
            'payment': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to mark payment as collected: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentDetailView(generics.RetrieveAPIView):
    """
    Retrieve payment details
    """
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user)
