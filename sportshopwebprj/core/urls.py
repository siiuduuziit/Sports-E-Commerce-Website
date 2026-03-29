from django.urls import path, include
from . import views


app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('products/', views.products_categories, name='products'),
    path('product/<str:pid>/', views.product_details, name='product-details'),
    path('ajax-add-review/<str:pid>/', views.ajax_add_review, name='ajax-add-review'),
    path('search/', views.search, name='search'),
    path('filter-products/', views.filter_products, name='filter-products'),
    path('add-to-cart/', views.add_to_cart, name='add-to-cart'),
    path('shopping-cart/', views.cart, name='shopping-cart'),
    path('delete-from-cart/', views.delete_from_cart, name='delete-from-cart'),
    path('update-cart/', views.update_cart, name='update-cart'),
    path('checkout/', views.checkout, name='checkout'),
    # path('create-order/', views.create_order, name='create-order'),
    path('account-details/', views.account_details, name='account-details'),
    path('account-details/order-details/<int:id>/', views.order_details, name='order-details'),
    path('make-default-address/', views.make_default_address, name='make-default-address'),
    # path('wishlists/', views.wishlists, name='wishlists'),
    path('add-to-wishlist/', views.add_to_wishlist, name='add-to-wishlist'),
    path('remove-from-wishlist/', views.remove_from_wishlist, name='remove-from-wishlist'),
    path('contact-us/', views.contact_us, name='contact-us'),
    path('ajax-contact-us/', views.ajax_contact_us, name='ajax-contact-us'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('about/', views.about, name='about'),
    path('redeem-coupon/<int:id>', views.redeem_coupon, name='redeem-coupon'),
]
