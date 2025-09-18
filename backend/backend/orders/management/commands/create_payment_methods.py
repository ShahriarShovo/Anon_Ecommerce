from django.core.management.base import BaseCommand
from orders.models.payments.payment_method import PaymentMethod


class Command(BaseCommand):
    help = 'Create default payment methods'

    def handle(self, *args, **options):
        # Create Cash on Delivery payment method
        cod_method, created = PaymentMethod.objects.get_or_create(
            method_type='cash_on_delivery',
            defaults={
                'name': 'Cash on Delivery',
                'description': 'Pay when your order is delivered',
                'is_active': True,
                'is_cod': True,
                'processing_fee': 0.00,
                'processing_fee_type': 'fixed',
                'display_order': 1,
                'icon': 'cash'
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created Cash on Delivery payment method')
            )
        else:
            self.stdout.write('Cash on Delivery payment method already exists')

        # Create bKash payment method
        bkash_method, created = PaymentMethod.objects.get_or_create(
            method_type='bkash',
            defaults={
                'name': 'bKash Payment',
                'description': 'Pay using bKash mobile banking',
                'is_active': True,
                'is_cod': False,
                'processing_fee': 0.00,
                'processing_fee_type': 'fixed',
                'display_order': 2,
                'icon': 'mobile'
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created bKash payment method')
            )
        else:
            self.stdout.write('bKash payment method already exists')

        self.stdout.write(
            self.style.SUCCESS('Payment methods setup completed!')
        )
