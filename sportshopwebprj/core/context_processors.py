# from .models import Category, Product, Wishlist


# def global_data(request):

#     categories = Category.objects.all().order_by('ctitle')

#     cart_sub_total_amount = 0
#     cart_total_amount = 0

#     cart_data = request.session.get('cart_data_obj', {})

#     for product_id, item in cart_data.items():
#         price = float(item['price'].replace(',', ''))
#         qty = int(item['qty'])
#         cart_sub_total_amount += qty * price
#         cart_total_amount += qty * price

#     wishlist_ids = []
#     total_wishlist_items = 0   # ✅ DEFAULT

#     if request.user.is_authenticated:
#         wishlist_qs = Wishlist.objects.filter(user=request.user)

#         wishlist_ids = list(
#             wishlist_qs.values_list('product_id', flat=True)
#         )
#         total_wishlist_items = wishlist_qs.count()

#     return {
#         'categories': categories,
#         'cart_data': cart_data,
#         'cart_sub_total_amount': cart_sub_total_amount,
#         'cart_total_amount': cart_total_amount,
#         'wishlist_ids': wishlist_ids,
#         'total_wishlist_items': total_wishlist_items,
#     }


from .models import Category, Product, Wishlist, CartOrder
from django.db.models import Sum

def global_data(request):
    categories = Category.objects.all().order_by('ctitle')

    cart_sub_total_amount = 0
    cart_total_amount = 0
    cart_data = request.session.get('cart_data_obj', {})

    for product_id, item in cart_data.items():
        try:
            # Ép kiểu về string trước khi replace để tránh lỗi nếu price là float/int
            price_str = str(item['price']).replace(',', '')
            price = float(price_str)
            qty = int(item['qty'])
            cart_sub_total_amount += qty * price
            cart_total_amount += qty * price
        except (ValueError, TypeError, KeyError):
            continue

    wishlist_ids = []
    total_wishlist_items = 0

    if request.user.is_authenticated:
        wishlist_qs = Wishlist.objects.filter(user=request.user)
        wishlist_ids = list(wishlist_qs.values_list('product_id', flat=True))
        total_wishlist_items = wishlist_qs.count()

    # --- THÊM LOGIC THỐNG KÊ CHO ADMIN ---
    admin_stats = {}
    if request.user.is_staff:

        # 1. Đếm đơn hàng
        processing = CartOrder.objects.filter(product_status="Đang xử lý").count()
        paid = CartOrder.objects.filter(paid_status=True).count()
        cancelled = CartOrder.objects.filter(product_status="Hủy").count()
        
        # 2. Tính tổng doanh thu
        revenue_data = CartOrder.objects.filter(paid_status=True).aggregate(Sum('price'))
        # Ép về float để intcomma trong template dễ nhận diện
        total_revenue = float(revenue_data['price__sum'] or 0)

        # 3. Lấy 5 đơn mới nhất
        latest_orders = CartOrder.objects.all().order_by('-id')[:5]
        
        admin_stats = {
            'order_chart_data': [processing, paid, cancelled],
            'total_revenue': total_revenue, # Đã ép kiểu số
            'total_orders': CartOrder.objects.count(),
            'latest_orders': latest_orders,
        }

    return {
        'categories': categories,
        'cart_data': cart_data,
        'cart_sub_total_amount': cart_sub_total_amount,
        'cart_total_amount': cart_total_amount,
        'wishlist_ids': wishlist_ids,
        'total_wishlist_items': total_wishlist_items,
        'admin_stats': admin_stats,
    }
