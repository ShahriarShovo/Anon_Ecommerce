from django.core.management.base import BaseCommand
from products.models import Product, ProductVariant, ProductImage, Category, SubCategory, VariantOption

class Command(BaseCommand):
    help = 'Create test products with variants and images'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Creating test products...'))
        
        try:
            # Get or create category and subcategory
            category, created = Category.objects.get_or_create(
                name="Test Category",
                defaults={
                    'description': 'Test category for product testing',
                    'is_active': True
                }
            )
            self.stdout.write(f"Category: {'Created' if created else 'Found'} - {category.name}")
            
            subcategory, created = SubCategory.objects.get_or_create(
                name="Test SubCategory",
                defaults={
                    'category': category,
                    'description': 'Test subcategory for product testing',
                    'is_active': True
                }
            )
            self.stdout.write(f"SubCategory: {'Created' if created else 'Found'} - {subcategory.name}")
            
            # Create simple product
            simple_product = Product.objects.create(
                title="Test Simple Product",
                description="This is a test simple product created via management command",
                short_description="Test simple product",
                category=category,
                subcategory=subcategory,
                product_type="simple",
                status="active",
                price=25.99,
                old_price=35.99,
                track_quantity=True,
                quantity=100,
                allow_backorder=False,
                weight_unit="kg",
                requires_shipping=True,
                taxable=True,
                featured=False
            )
            self.stdout.write(self.style.SUCCESS(f"✅ Simple Product created: {simple_product.title} (ID: {simple_product.id})"))
            
            # Create variable product
            variable_product = Product.objects.create(
                title="Test Variable Product",
                description="This is a test variable product with variants",
                short_description="Test variable product",
                category=category,
                subcategory=subcategory,
                product_type="variable",
                status="active",
                price=15.00,
                old_price=25.00,
                track_quantity=True,
                quantity=50,
                allow_backorder=False,
                weight_unit="kg",
                requires_shipping=True,
                taxable=True,
                featured=False,
                option1_name="Size",
                option2_name="Color"
            )
            self.stdout.write(self.style.SUCCESS(f"✅ Variable Product created: {variable_product.title} (ID: {variable_product.id})"))
            
            # Create variants for variable product
            variant1 = ProductVariant.objects.create(
                product=variable_product,
                title="Small Red",
                sku="TEST-SMALL-RED",
                price=10.00,
                old_price=15.00,
                quantity=20,
                track_quantity=True,
                allow_backorder=False,
                weight_unit="kg",
                position=1,
                is_active=True,
                option1_name="Size",
                option1_value="Small",
                option2_name="Color",
                option2_value="Red"
            )
            self.stdout.write(self.style.SUCCESS(f"✅ Variant 1 created: {variant1.title} (ID: {variant1.id})"))
            
            # Add dynamic options to variant1
            VariantOption.objects.create(
                variant=variant1,
                name="Size",
                value="Small",
                position=1
            )
            VariantOption.objects.create(
                variant=variant1,
                name="Color",
                value="Red",
                position=2
            )
            self.stdout.write(self.style.SUCCESS("✅ Dynamic options added to variant 1"))
            
            variant2 = ProductVariant.objects.create(
                product=variable_product,
                title="Large Blue",
                sku="TEST-LARGE-BLUE",
                price=20.00,
                old_price=30.00,
                quantity=15,
                track_quantity=True,
                allow_backorder=False,
                weight_unit="kg",
                position=2,
                is_active=True,
                option1_name="Size",
                option1_value="Large",
                option2_name="Color",
                option2_value="Blue"
            )
            self.stdout.write(self.style.SUCCESS(f"✅ Variant 2 created: {variant2.title} (ID: {variant2.id})"))
            
            # Add dynamic options to variant2
            VariantOption.objects.create(
                variant=variant2,
                name="Size",
                value="Large",
                position=1
            )
            VariantOption.objects.create(
                variant=variant2,
                name="Color",
                value="Blue",
                position=2
            )
            self.stdout.write(self.style.SUCCESS("✅ Dynamic options added to variant 2"))
            
            # Test variant methods
            self.stdout.write("\n📊 Testing Variant Methods:")
            self.stdout.write(f"Variant 1 all_options: {variant1.get_all_options()}")
            self.stdout.write(f"Variant 1 dynamic_options: {variant1.get_dynamic_options()}")
            self.stdout.write(f"Variant 1 display_price: {variant1.display_price}")
            self.stdout.write(f"Variant 1 discount_percentage: {variant1.discount_percentage}")
            
            # Test product methods
            self.stdout.write("\n📊 Testing Product Methods:")
            self.stdout.write(f"Variable product primary_image: {variable_product.primary_image}")
            self.stdout.write(f"Variable product variant_count: {variable_product.variants.count()}")
            
            self.stdout.write(self.style.SUCCESS("\n✅ All test data created successfully!"))
            self.stdout.write("📋 Summary:")
            self.stdout.write(f"  - Simple Product: {simple_product.title} (ID: {simple_product.id})")
            self.stdout.write(f"  - Variable Product: {variable_product.title} (ID: {variable_product.id})")
            self.stdout.write(f"  - Variants: {variable_product.variants.count()}")
            self.stdout.write(f"  - Dynamic Options: {VariantOption.objects.count()}")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error creating test data: {e}"))
            import traceback
            traceback.print_exc()
