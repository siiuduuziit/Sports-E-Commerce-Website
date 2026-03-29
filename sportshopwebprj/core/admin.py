from django.contrib import admin
from .models import Category, Vendor, Product, CartOrder, CartOrderItem, ProductGallery, ProductReview, Wishlist, Address, Coupon, ChatbotFAQ, ChatbotLog, UserCoupon, Profile


admin.site.site_header = "Dang Sport Shop Admin"
admin.site.site_header = "Dang Sport Shop Admin Portal"
admin.site.index_title = "Welcome to Dang Sport Shop Admin Portal"
admin.site.site_title = "Dang Sport Shop Admin Portal"


class ProductGalleryAdmin(admin.TabularInline):
    model = ProductGallery


class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductGalleryAdmin]
    list_display = ('user', 'title', 'category', 'product_image', 'price', 'featured', 'product_status', 'pid')
    list_filter = ('featured', 'product_status')
    search_fields = ('title', 'description')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('ctitle', 'category_image')
    list_filter = ('ctitle',)
    search_fields = ('ctitle',)


class VendorAdmin(admin.ModelAdmin):
    list_display = ('title', 'vendor_image')
    list_filter = ('title',)
    search_fields = ('title',)


class CartOrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'price', 'paid_status', 'order_date')
    list_filter = ('paid_status', 'product_status')
    search_fields = ('user__username',)


class CartOrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'invoice', 'item', 'image', 'quantity', 'price', 'total')
    list_filter = ('order',)
    search_fields = ('invoice',)


class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'review', 'date')
    list_filter = ('rating',)
    search_fields = ('user__username', 'product__title')


class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'date_added')
    list_filter = ('date_added',)
    search_fields = ('user__username', 'product__title')


class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'address_name', 'address_line', 'address_status')
    list_filter = ('address_status',)
    search_fields = ('user__username', 'address_line')


class CouponAdmin(admin.ModelAdmin):
    list_display = ('coupon', 'discount', 'points_required', 'active')
    list_filter = ('points_required', 'active')
    search_fields = ('points_required', 'coupon')


class UserCouponAdmin(admin.ModelAdmin):
    list_display = ('user', 'coupon', 'redeemed_at')
    list_filter = ('user', 'coupon', 'redeemed_at')
    search_fields = ('user', 'coupon', 'redeemed_at')


class ProfilePointAdmin(admin.ModelAdmin):
    list_display = ('user', 'points')
    list_filter = ('user', 'points')
    search_fields = ('user',)


class ChatbotFAQAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'answer')
    list_filter = ('keyword',)
    search_fields = ('keyword',)


class ChatbotLogAdmin(admin.ModelAdmin):
    list_display = ('message', 'matched_product', 'created_at')
    list_filter = ('message',)
    search_fields = ('created_at',)


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Vendor, VendorAdmin)
admin.site.register(CartOrder, CartOrderAdmin)
admin.site.register(CartOrderItem, CartOrderItemAdmin)
admin.site.register(ProductReview, ProductReviewAdmin)
admin.site.register(Wishlist, WishlistAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(UserCoupon, UserCouponAdmin)
admin.site.register(Profile, ProfilePointAdmin)
admin.site.register(ChatbotFAQ, ChatbotFAQAdmin)
admin.site.register(ChatbotLog, ChatbotLogAdmin)
