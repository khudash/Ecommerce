from django.contrib import admin
from .models import Benefit, Hero, Product, Order, OrderItem, FormulaSection, ContactMessage, Review, ReviewSectionSettings, BlogPost

@admin.register(Hero)
class HeroAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Main Content', {
            'fields': ('heading', 'heading_green', 'sub_heading', 'image')
        }),
        ('Button', {
            'fields': ('button_text', 'button_link')
        }),
        ('Top Badge', {
            'fields': ('badge_text',)
        }),
        ('Trust Points (Checkmarks)', {
            'fields': ('trust_point_1', 'trust_point_2', 'trust_point_3')
        }),
        ('Floating Card (Bottom Left)', {
            'fields': ('floating_card_label', 'floating_card_value')
        }),
        ('Rating Card (Top Right)', {
            'fields': ('rating_card_text',)
        }),
    )

admin.site.register(FormulaSection)

@admin.register(ReviewSectionSettings)
class ReviewSectionSettingsAdmin(admin.ModelAdmin):
    list_display = ('heading', 'heading_green', 'rating_score', 'total_reviews_text')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'rating', 'verified_badge', 'city', 'is_approved', 'is_featured', 'order', 'created_at')
    list_filter = ('rating', 'is_approved', 'is_featured', 'created_at')
    search_fields = ('name', 'comment', 'city', 'verified_badge')
    list_editable = ('is_approved', 'is_featured', 'order')

@admin.register(Benefit)
class BenefitAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon', 'description')
    search_fields = ('title', 'description', 'icon')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "size",
        "price",
        "old_price",
        "discount",
        "badge",
        "is_featured",
        "is_available",
    )
    list_filter = ("is_available", "is_featured", "size")
    search_fields = ("name", "size", "description", "badge")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'quantity', 'price', 'item_total')
    fields = ('product_name', 'quantity', 'price', 'item_total')

    def item_total(self, obj):
        return f"Rs. {obj.price * obj.quantity:.0f}"
    item_total.short_description = "Item Total"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'phone', 'city', 'postal_code', 'payment_method', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('full_name', 'phone', 'email', 'transaction_id')
    inlines = [OrderItemInline]


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'subject', 'created_at')
    search_fields = ('name', 'email', 'phone', 'subject', 'message')
    list_filter = ('created_at',)