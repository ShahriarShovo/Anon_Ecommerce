from django.contrib import admin
from django.contrib.auth.models import Permission
from products.models import Category, SubCategory, Product, ProductVariant, ProductImage, VariantOption, ProductReview, ReviewVote

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at', 'subcategories_count']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    
    def subcategories_count(self, obj):
        return obj.subcategories.count()
    subcategories_count.short_description = 'SubCategories Count'

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'slug', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'category__name']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    list_select_related = ['category']

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'caption', 'position', 'is_primary']

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ['title', 'sku', 'price', 'old_price', 'quantity', 'is_active']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'status', 'category', 'price', 'quantity', 'featured', 'created_at']
    list_filter = ['status', 'category', 'subcategory', 'featured', 'created_at']
    search_fields = ['title', 'slug', 'description', 'tags']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at', 'published_at']
    inlines = [ProductImageInline, ProductVariantInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'short_description')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Categorization', {
            'fields': ('category', 'subcategory', 'product_type', 'status')
        }),
        ('Pricing', {
            'fields': ('price', 'old_price')
        }),
        ('Inventory', {
            'fields': ('track_quantity', 'quantity', 'allow_backorder', 'quantity_policy')
        }),
        ('Physical Properties', {
            'fields': ('weight', 'weight_unit', 'requires_shipping', 'taxable')
        }),
        ('Marketing', {
            'fields': ('featured', 'tags')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['title', 'product', 'sku', 'price', 'quantity', 'is_active']
    list_filter = ['is_active', 'product__category', 'created_at']
    search_fields = ['title', 'sku', 'barcode', 'product__title']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'position', 'is_primary', 'created_at']
    list_filter = ['is_primary', 'product__category', 'created_at']
    search_fields = ['product__title', 'alt_text', 'caption']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(VariantOption)
class VariantOptionAdmin(admin.ModelAdmin):
    list_display = ['variant', 'name', 'value', 'position']
    list_filter = ['name', 'variant__product__category']
    search_fields = ['name', 'value', 'variant__title', 'variant__product__title']
    ordering = ['variant', 'position']

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'display_name', 'rating', 'title', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'is_verified_purchase', 'created_at']
    search_fields = ['product__title', 'title', 'comment', 'user_name', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    list_select_related = ['product', 'user']
    
    fieldsets = (
        ('Review Information', {
            'fields': ('product', 'user', 'rating', 'title', 'comment')
        }),
        ('User Information', {
            'fields': ('user_name', 'user_email'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_approved', 'is_verified_purchase', 'helpful_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ReviewVote)
class ReviewVoteAdmin(admin.ModelAdmin):
    list_display = ['review', 'user', 'is_helpful', 'created_at']
    list_filter = ['is_helpful', 'created_at']
    search_fields = ['review__product__title', 'user__username']
    readonly_fields = ['created_at']
    list_select_related = ['review', 'user']
