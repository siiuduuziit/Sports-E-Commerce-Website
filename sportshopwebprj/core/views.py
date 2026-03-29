import calendar
import json

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .models import Product, Category, Vendor, ProductGallery, CartOrder, CartOrderItem, ProductReview, Wishlist, Address, Coupon, ChatbotFAQ, ChatbotLog, Profile, UserCoupon
from userauths.models import ContactUs
from .forms import ProductReviewForm
from django.db.models import Min, Max, Count
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.humanize.templatetags.humanize import intcomma
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.db.models.functions import ExtractMonth
from django.views.decorators.csrf import csrf_exempt
from core.chatbot.utils import calculate_match_score, product_to_dict
from core.chatbot.constants import PRICE_KEYWORDS, STOCK_KEYWORDS, LIST_KEYWORDS, SIMILAR_KEYWORDS, STOP_KEYWORDS
from core.chatbot.handlers import handle_price, handle_stock, handle_similar
from core.chatbot.services import get_best_product, get_similar_products
from core.chatbot.chatbotlog import save_chat_log
from core.chatbot.ai_service import ai_understand
from django.conf import settings
from django.core.mail import EmailMessage, send_mail
from django.db.models import Q, F


def index(request):

    products = Product.objects.filter(product_status='available', featured=True).order_by('-id')[:8]

    context = {
        'products': products,
    }

    return render(request, 'core/index.html', context)


def products_categories(request):

    products = Product.objects.filter(product_status='available').order_by('-id')
    min_max_price = Product.objects.aggregate(Min('price'), Max('price'))

    context = {
        'products': products,
        'min_max_price': min_max_price,
    }

    return render(request, 'core/products.html', context)


def product_details(request, pid):

    product = Product.objects.get(pid=pid)
    category = product.category
    p_images = product.p_images.all()
    related_products = Product.objects.filter(category=product.category).exclude(pid=pid)[:8]
    reviews = ProductReview.objects.filter(product=product).order_by('-date')
    review_form = ProductReviewForm()

    context = {
        'product': product,
        'category': category,
        'p_images': p_images,
        'related_products': related_products,
        'reviews': reviews,
        'review_form': review_form,
    }

    return render(request, 'core/product_details.html', context)


@login_required
def ajax_add_review(request, pid):
    if request.method == "POST":
        product = Product.objects.get(pid=pid)
        
        # Lấy từ <select name="rating">
        rating_val = request.POST.get('rating')
        if not rating_val:
            rating_val = 5
            
        review = ProductReview.objects.create(
            product=product,
            user=request.user,
            review=request.POST.get('review'),
            rating=int(rating_val), 
        )

        # --- Gửi email xác nhận tới user ---
        subject = f"Cảm ơn bạn đã đánh giá sản phẩm {product.title}"
        message = f"Xin chào {request.user.username},\n\n" \
                  f"Cảm ơn bạn đã gửi phản hồi cho sản phẩm '{product.title}'.\n" \
                  f"Điểm đánh giá: {review.rating}\n" \
                  f"Nội dung: {review.review}\n\n" \
                  f"Chúng tôi trân trọng ý kiến của bạn!"
        recipient = [request.user.email]

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            recipient,
            fail_silently=False,
        )

        return JsonResponse({
            'bool': True,
            'context': {
                'user': request.user.username,
                'review': review.review,
                'rating': review.rating,
            }
        })


def search(request):
    
    query = request.GET.get("search")
    
    # Lấy lại các thông tin bổ trợ để Filter không bị lỗi giao diện
    min_max_price = Product.objects.aggregate(Min("price"), Max("price"))

    if query:
        words = query.split()
        q_objects = Q()
        for word in words:
            # Dùng &= (AND) nếu muốn tìm chính xác các từ đi cùng nhau
            # Dùng |= (OR) nếu muốn tìm bất kỳ từ nào có trong title
            q_objects |= Q(title__icontains=word) | Q(description__icontains=word)
            
        searched_product = Product.objects.filter(q_objects).distinct().order_by("-date")
    else:
        searched_product = Product.objects.none()

    context = {
        'query': query,
        'searched_product': searched_product, # Đảm bảo tên này khớp với template
        'min_max_price': min_max_price,
    }

    return render(request, 'core/search.html', context)


def filter_products(request):

    # Lấy dữ liệu an toàn
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort_by = request.GET.get('sort')

    # Query gốc
    products = Product.objects.filter(product_status='available')

    # Lọc theo price (nếu có gửi)
    if min_price:
        products = products.filter(price__gte=min_price)

    if max_price:
        products = products.filter(price__lte=max_price)

    # Sắp xếp theo sort_by
    if sort_by == "newest":
        products = products.order_by("-id")
    elif sort_by == "price_asc":
        products = products.order_by("price")
    elif sort_by == "price_desc":
        products = products.order_by("-price")
    else:
        products = products.order_by("-id")  # default

    # Render ra HTML để replace
    data = render_to_string("core/async/products.html", {"products": products})

    return JsonResponse({"data": data})


def cart(request):

    # Lấy cart an toàn
    cart_data = request.session.get('cart_data_obj', {})

    # Tính tổng
    cart_sub_total_amount = 0.0
    cart_total_amount = 0.0

    for product_id, item in cart_data.items():
        try:
            price = float(str(item.get('price', '0')).replace(',', '').strip() or 0)
        except ValueError:
            price = 0.0
        try:
            qty = int(item.get('qty', 0))
        except (ValueError, TypeError):
            qty = 0

        cart_sub_total_amount += qty * price
        cart_total_amount += qty * price

    context = {
        'cart_data': cart_data,
        'total_cart_items': len(cart_data),
        'cart_sub_total_amount': cart_sub_total_amount,
        'cart_total_amount': cart_total_amount,
    }

    return render(request, 'core/shopping_cart.html', context)


@login_required
def add_to_cart(request):

    # lấy cart trong session, nếu chưa có thì tạo cart rỗng
    cart_data = request.session.get('cart_data_obj', {})

    product_id = str(request.GET.get('id'))

    # nếu sản phẩm đã có trong cart → tăng qty
    if product_id in cart_data:
        cart_data[product_id]['qty'] += int(request.GET.get('qty'))
    else:
        # thêm sản phẩm mới
        cart_data[product_id] = {
            'pid': request.GET.get('pid'),
            'title': request.GET.get('title'),
            'qty': int(request.GET.get('qty')),
            'price': request.GET.get('price'),
            'image': request.GET.get('image'),
        }

    # save cart back
    request.session['cart_data_obj'] = cart_data

    # tính total
    cart_total_amount = 0
    for _, item in cart_data.items():
        cart_total_amount += item['qty'] * float(item['price'].replace(',', ''))

    # render mini-cart HTML
    mini_cart_html = render_to_string('core/async/mini_cart.html', {
        'cart_data': cart_data,
        'cart_total_amount': cart_total_amount,
    })

    return JsonResponse({
        'total_cart_items': len(cart_data),
        'mini_cart_html': mini_cart_html,
    })


def delete_from_cart(request):

    cart_data = request.session.get('cart_data_obj', {})
    product_id = str(request.GET.get('id'))

    # Xóa sản phẩm
    if product_id in cart_data:
        del cart_data[product_id]

    # Lưu lại session
    request.session['cart_data_obj'] = cart_data

    # Tính tổng
    cart_sub_total_amount = 0.0
    cart_total_amount = 0.0

    for product_id, item in cart_data.items():
        try:
            price = float(str(item.get('price', '0')).replace(',', '').strip())
        except:
            price = 0.0
        qty = int(item.get('qty', 0))

        cart_sub_total_amount += qty * price
        cart_total_amount += qty * price

    # Render partial cart HTML
    html = render_to_string('core/async/shopping_cart.html', {
        'cart_data': cart_data,
        'total_cart_items': len(cart_data),
        'cart_sub_total_amount': cart_sub_total_amount,
        'cart_total_amount': cart_total_amount,
    })

    return JsonResponse({
        'data': html,
        'total_cart_items': len(cart_data),
        'cart_sub_total_amount': intcomma(cart_sub_total_amount),
        'cart_total_amount': intcomma(cart_total_amount),
    })


def update_cart(request):

    cart_data = request.session.get('cart_data_obj', {})

    product_id = str(request.GET.get('id'))
    qty = int(request.GET.get('qty', 1))

    # Update số lượng
    if product_id in cart_data:
        cart_data[product_id]['qty'] = qty

    # Lưu lại session
    request.session['cart_data_obj'] = cart_data

    # Tính tổng
    cart_sub_total_amount = 0.0
    cart_total_amount = 0.0

    for pid, item in cart_data.items():
        try:
            price = float(str(item.get('price', '0')).replace(',', '').strip())
        except:
            price = 0.0
        qty = int(item.get('qty', 0))

        cart_sub_total_amount += qty * price
        cart_total_amount += qty * price

    # Render partial cart HTML
    html = render_to_string('core/async/shopping_cart.html', {
        'cart_data': cart_data,
        'total_cart_items': len(cart_data),
        'cart_sub_total_amount': cart_sub_total_amount,
        'cart_total_amount': cart_total_amount,
    })

    return JsonResponse({
        'data': html,
        'total_cart_items': len(cart_data),
        'cart_sub_total_amount': intcomma(cart_sub_total_amount),
        'cart_total_amount': intcomma(cart_total_amount),
    })


@login_required
def checkout(request):
    cart_data = request.session.get('cart_data_obj', {})
    if not cart_data:
        return redirect('core:index')

    # =====================
    # CALCULATE CART
    # =====================
    cart_sub_total = 0
    for item in cart_data.values():
        price = float(item['price'].replace(',', ''))
        qty = int(item['qty'])
        cart_sub_total += price * qty

    discount = request.session.get('discount', 0)
    cart_total = max(cart_sub_total - discount, 0)

    # =====================
    # HANDLE POST
    # =====================
    if request.method == 'POST':
        action = request.POST.get('action')

        # APPLY COUPON
        if action == 'coupon':
            code = request.POST.get('coupon_code', '').strip()
            coupon = Coupon.objects.filter(coupon=code, active=True).first()

            if coupon:
                # CHẶN BUG TẠI ĐÂY: Kiểm tra xem User đã đổi điểm lấy mã này chưa
                # Nếu coupon này yêu cầu điểm (>0), thì phải có bản ghi trong UserCoupon
                user_owned = True
                if coupon.points_required > 0:
                    user_owned = UserCoupon.objects.filter(
                        user=request.user, 
                        coupon=coupon, 
                        used=False # Chỉ cho áp dụng nếu mã chưa bị dùng
                    ).exists()

                if user_owned:
                    discount = cart_sub_total * coupon.discount / 100
                    request.session['discount'] = discount
                    request.session['coupon_code'] = code
                    messages.success(request, f'Áp dụng coupon {code} thành công!')
                else:
                    messages.error(request, 'Bạn chưa đổi điểm để sở hữu mã giảm giá này.')
            else:
                messages.error(request, 'Coupon không hợp lệ hoặc đã hết hạn.')

            return redirect('core:checkout')

        # CREATE ORDER (COD / BANK)
        if action in ['cod', 'bank']:
            order = CartOrder.objects.create(
                user=request.user,
                price=cart_total,
                full_name=request.POST.get('full_name'),
                email=request.POST.get('email'),
                province_name=request.POST.get('province_name'),
                district_name=request.POST.get('district_name'),
                ward_name=request.POST.get('ward_name'),
                address_line=request.POST.get('address_line'),
                phone_number=request.POST.get('phone_number'),
                notes=request.POST.get('notes'),
                paid_status=False,  # an toàn
                payment_method=action
            )

            points_earned = int(cart_total / 10000)

            user_profile, created = Profile.objects.get_or_create(user=request.user)
            user_profile.points += points_earned
            user_profile.save()

            coupon_code = request.session.get('coupon_code')
            if coupon_code:
                # Tìm mã và đánh dấu là đã dùng
                UserCoupon.objects.filter(
                    user=request.user, 
                    coupon__coupon=coupon_code, 
                    used=False
                ).update(used=True)

            # Create order items
            order_items = []
            for item in cart_data.values():
                price = float(item['price'].replace(',', ''))
                qty = int(item['qty'])

                order_item = CartOrderItem.objects.create(
                    order=order,
                    item=item['title'],
                    image=item['image'],
                    quantity=qty,
                    price=price,
                    total=price * qty,
                    product_status="Đang xử lý",
                    invoice=f"INV-{order.id}"
                )
                order_items.append(order_item)

            # =====================
            # SEND EMAIL HÓA ĐƠN
            # =====================
            subject = f"Hóa đơn mua hàng #{order.id}"
            recipient = [request.user.email]

            # Tạo nội dung HTML bằng template
            message_html = render_to_string('emails/order_invoice.html', {
                'order': order,
                'order_items': order_items,
                'cart_total': cart_total,
                'discount': discount,
            })

            email = EmailMessage(
                subject=subject,
                body=message_html,
                from_email=settings.EMAIL_HOST_USER,
                to=recipient,
            )
            email.content_subtype = "html"  # gửi HTML
            email.send(fail_silently=False)

            # Clear session
            request.session.pop('cart_data_obj', None)
            request.session.pop('discount', None)
            request.session.pop('coupon_code', None)

            return redirect('core:index')

    # GET ACTIVE ADDRESS
    active_address = Address.objects.filter(
        user=request.user,
        address_status=True
    ).first()

    return render(request, 'core/checkout.html', {
        'cart_data': cart_data,
        'cart_sub_total_amount': cart_sub_total,
        'cart_total_amount': cart_total,
        'cart_total_amount_int': int(cart_total),
        'discount': discount,
        'active_address': active_address,
    })


@login_required
def account_details(request):

    orders = CartOrder.objects.filter(user=request.user).order_by('-id')
    addresses = Address.objects.filter(user=request.user)
    wishlists = Wishlist.objects.filter(user=request.user)
    coupons = Coupon.objects.filter(active=True)
    user_owned_ids = list(UserCoupon.objects.filter(user=request.user).values_list('coupon_id', flat=True))

    user_points = request.user.profile.points

    coupon_data = []
    for coupon in coupons:
        need_points = max(0, coupon.points_required - user_points)

        coupon_data.append({
            "coupon": coupon,
            "need_points": need_points,
            "can_redeem": user_points >= coupon.points_required,
        })


    orders_chart = CartOrder.objects.filter(user=request.user).annotate(month=ExtractMonth('order_date')).values('month').annotate(count=Count('id')).values('month', 'count')
    month_list = []
    total_orders_list = []

    for order in orders_chart:
        month_list.append(calendar.month_name[order['month']])
        total_orders_list.append(order['count'])

    month_json = json.dumps(month_list)
    total_orders_json = json.dumps(total_orders_list)

    if request.method == 'POST':
        name = request.POST.get('name')
        address = request.POST.get('address')
        phone_number = request.POST.get('phone_number')

        new_address = Address.objects.create(
            user=request.user,
            address_name=name,
            address_line=address,
            phone_number=phone_number,
        )

        messages.success(request, 'New address added')
        return redirect('core:account-details')

    context = {
        'orders': orders,
        'addresses': addresses,
        'wishlists': wishlists,
        'orders_chart': orders_chart,
        'month_json': month_json,
        'total_orders_json': total_orders_json,
        'coupons': coupons,
        'user_owned_ids': user_owned_ids,
        'coupon_data': coupon_data,
    }
    
    return render(request, 'core/account_details.html', context)


@login_required
def order_details(request, id):
    # Lấy thông tin đơn hàng
    order = CartOrder.objects.get(user=request.user, id=id)
    # Lấy danh sách sản phẩm trong đơn hàng đó
    order_items = CartOrderItem.objects.filter(order=order)
    addresses = Address.objects.filter(user=request.user)

    context = {
        'order': order,         # QUAN TRỌNG: Phải có dòng này
        'order_items': order_items,
        'addresses': addresses,
    }

    return render(request, 'core/order_details.html', context)


def make_default_address(request):

    id = str(request.GET.get('id'))

    Address.objects.filter(user=request.user).update(address_status=False)
    Address.objects.filter(id=id, user=request.user).update(address_status=True)

    return JsonResponse({
        'boolean': True,
    })


def add_to_wishlist(request):

    product_id = str(request.GET.get('id'))
    
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        # Xử lý trường hợp không tìm thấy sản phẩm
        return JsonResponse({'status': 'error', 'message': 'Product not found'}, status=404)

    # 1. Kiểm tra sản phẩm đã có trong Wishlist chưa
    wishlist_item = Wishlist.objects.filter(user=request.user, product=product)
    
    added = False
    
    if wishlist_item.exists():
        # Nếu đã có (wishlist_count > 0) -> XÓA (Toggle)
        wishlist_item.delete()
        message = f'"{product.title}" removed from your Wishlist.'
        added = False # Đánh dấu là đã xóa
    else:
        # Nếu chưa có -> THÊM vào
        Wishlist.objects.create(
            user=request.user,
            product=product,
        )
        message = f'"{product.title}" added to your Wishlist.'
        added = True # Đánh dấu là đã thêm
    
    # 2. Tính lại tổng số lượng Wishlist hiện tại
    total_wishlist_items = Wishlist.objects.filter(user=request.user).count()

    # 3. Trả về JSON để cập nhật giao diện
    return JsonResponse({
        'status': 'success',
        'message': message,
        'added': added, # Dùng để JS biết là đã Thêm hay Xóa
        'total_wishlist_items': total_wishlist_items, # Số lượng mới để cập nhật data-notify
    })


@login_required
def remove_from_wishlist(request):
    if request.method == 'POST':
        wishlist_id = request.POST.get('id')

        Wishlist.objects.filter(
            id=wishlist_id,
            user=request.user
        ).delete()

        total = Wishlist.objects.filter(user=request.user).count()

        return JsonResponse({
            'status': 'success',
            'total_wishlist_items': total
        })


def contact_us(request):

    return render(request, 'core/contact_us.html')


def ajax_contact_us(request):
    if request.method == "POST":
        email = request.POST.get('email')
        full_name = request.POST.get('full_name')
        subject = request.POST.get('subject')
        message = request.POST.get('msg')

        # Lưu contact vào database
        ContactUs.objects.create(
            email=email,
            full_name=full_name,
            subject=subject,
            message=message,
        )

        # Render template email
        message_html = render_to_string('emails/contact_response.html', {
            'full_name': full_name,
            'message': message,
        })

        # Gửi email phản hồi
        email_msg = EmailMessage(
            subject=f"Cảm ơn bạn đã liên hệ: {subject}",
            body=message_html,
            from_email=settings.EMAIL_HOST_USER,
            to=[email],
        )
        email_msg.content_subtype = "html"  # dùng HTML
        email_msg.send(fail_silently=True)

        return JsonResponse({'bool': True})
    else:
        return JsonResponse({'bool': False, 'error': 'Invalid request'})


# @csrf_exempt
# def chatbot(request):
#     if request.method != 'POST':
#         return JsonResponse({'error': 'Invalid request'}, status=400)

#     message = request.POST.get('message', '').lower()
#     products = Product.objects.all()

#     # ===== FAQ =====
#     for faq in ChatbotFAQ.objects.all():
#         for k in faq.keyword.split(','):
#             if k.strip().lower() in message:
#                 save_chat_log(message)
#                 return JsonResponse({
#                     "type": "text",
#                     "data": faq.answer
#                 })

#     # ===== STOP =====
#     if any(k in message for k in STOP_KEYWORDS):
#         request.session.pop('last_product_pid', None)
#         save_chat_log(message)
#         return JsonResponse({
#             "type": "text",
#             "data": "Ok nha! Khi nào cần cứ nhắn mình! 😊"
#         })

#     # ===== FIND PRODUCT (rule-based) =====
#     best_product = get_best_product(products, message, calculate_match_score)

#     if best_product:
#         request.session['last_product_pid'] = best_product.pid
#     else:
#         last_pid = request.session.get('last_product_pid')
#         if last_pid:
#             best_product = Product.objects.filter(pid=last_pid).first()

#     # ===== LIST =====
#     if any(k in message for k in LIST_KEYWORDS):
#         request.session.pop('last_product_pid', None)
#         save_chat_log(message)
#         return JsonResponse({
#             "type": "products",
#             "data": [product_to_dict(p) for p in products[:6]],
#             "message": "Shop đang có những sản phẩm nổi bật nè 👟"
#         })

#     # ===== PRICE =====
#     if best_product and any(k in message for k in PRICE_KEYWORDS):
#         save_chat_log(message, best_product)
#         return handle_price(message, product_to_dict(best_product))

#     # ===== SIMILAR =====
#     if best_product and any(k in message for k in SIMILAR_KEYWORDS):
#         save_chat_log(message, best_product)
#         return handle_similar(best_product)

#     # ===== STOCK =====
#     if best_product and any(k in message for k in STOCK_KEYWORDS):
#         save_chat_log(message, best_product)
#         return handle_stock(
#             message,
#             product_to_dict(best_product),
#             best_product.stock
#         )

#     # =================================================
#     # ================= AI HYBRID =====================
#     # =================================================
#     ai_data = ai_understand(message)

#     intent = ai_data.get("intent")
#     product_name = ai_data.get("product_name")

#     if intent and intent != "unknown":

#         # AI tìm product nếu có tên
#         if product_name:
#             best_product = Product.objects.filter(
#                 title__icontains=product_name
#             ).first()

#             if best_product:
#                 request.session['last_product_pid'] = best_product.pid

#         if intent == "list":
#             return JsonResponse({
#                 "type": "products",
#                 "data": [product_to_dict(p) for p in products[:6]],
#                 "message": "Mình gợi ý mấy mẫu này cho bạn nè 👟"
#             })

#         if best_product:
#             save_chat_log(message, best_product)

#             if intent == "price":
#                 return handle_price(message, product_to_dict(best_product))

#             if intent == "stock":
#                 return handle_stock(
#                     message,
#                     product_to_dict(best_product),
#                     best_product.stock
#                 )

#             if intent == "similar":
#                 return handle_similar(best_product)


#     # ===== FALLBACK PRODUCT =====
#     if best_product:
#         save_chat_log(message, best_product)
#         return JsonResponse({
#             "type": "product",
#             "data": product_to_dict(best_product),
#             "message": "Bạn muốn hỏi về giá, tồn kho hay xem mẫu tương tự nè?"
#         })

#     # ===== FINAL FALLBACK =====
#     save_chat_log(message)
#     return JsonResponse({
#         "type": "text",
#         "data": "Mình chưa hiểu lắm! Bạn nói rõ hơn giúp mình nha! 😥"
#     })


@csrf_exempt
def chatbot(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    message = request.POST.get('message', '').lower()
    products = Product.objects.all()
    best_product = None

    # 1. ===== FAQ (Rule-based) =====
    for faq in ChatbotFAQ.objects.all():
        for k in faq.keyword.split(','):
            if k.strip().lower() in message:
                save_chat_log(message)
                return JsonResponse({"type": "text", "data": faq.answer})

    # 2. ===== STOP =====
    if any(k in message for k in STOP_KEYWORDS):
        request.session.pop('last_product_pid', None)
        save_chat_log(message)
        return JsonResponse({"type": "text", "data": "Ok nha! Khi nào cần cứ nhắn mình! 😊"})

    # 3. ===== TÌM SẢN PHẨM (Rule-based) =====
    best_product = get_best_product(products, message, calculate_match_score)

    # 4. ===== XỬ LÝ THEO KEYWORD (Nhanh, không tốn AI) =====
    # Nếu tìm thấy product bằng rule hoặc từ session cũ
    if not best_product:
        last_pid = request.session.get('last_product_pid')
        if last_pid:
            best_product = Product.objects.filter(pid=last_pid).first()

    if any(k in message for k in LIST_KEYWORDS):
        request.session.pop('last_product_pid', None)
        return JsonResponse({
            "type": "products",
            "data": [product_to_dict(p) for p in products[:6]],
            "message": "Shop đang có những sản phẩm nổi bật nè 👟"
        })

    if best_product:
        if any(k in message for k in PRICE_KEYWORDS):
            return handle_price(message, product_to_dict(best_product))
        if any(k in message for k in SIMILAR_KEYWORDS):
            return handle_similar(best_product)
        if any(k in message for k in STOCK_KEYWORDS):
            return handle_stock(message, product_to_dict(best_product), best_product.stock)

    # 5. ================= AI HYBRID =====================
    # Chỉ gọi AI khi các rule cơ bản ở trên không khớp hoàn toàn
    ai_data = ai_understand(message)
    intent = ai_data.get("intent")
    p_name_ai = ai_data.get("product_name")

    if intent and intent != "unknown":
        # AI tìm tên sản phẩm giúp mình
        if p_name_ai:
            found = Product.objects.filter(title__icontains=p_name_ai).first()
            if found:
                best_product = found
                request.session['last_product_pid'] = best_product.pid

        # Nếu là intent xem danh sách
        if intent == "list":
            return JsonResponse({
                "type": "products",
                "data": [product_to_dict(p) for p in products[:6]],
                "message": "Mình gợi ý mấy mẫu này cho bạn nè 👟"
            })

        # Xử lý các intent khác nếu đã có best_product
        if best_product:
            save_chat_log(message, best_product)
            if intent == "price":
                return handle_price(message, product_to_dict(best_product))
            if intent == "stock":
                return handle_stock(message, product_to_dict(best_product), best_product.stock)
            if intent == "similar":
                return handle_similar(best_product)

    # 6. ===== FALLBACK (Khi vẫn tìm thấy giày nhưng chưa rõ ý định) =====
    if best_product:
        save_chat_log(message, best_product)
        return JsonResponse({
            "type": "product",
            "data": product_to_dict(best_product),
            "message": f"Bạn đang quan tâm mẫu {best_product.title} đúng không? Bạn muốn hỏi giá hay size nè?"
        })

    # 7. ===== FINAL FALLBACK =====
    save_chat_log(message)
    return JsonResponse({
        "type": "text",
        "data": "Mình chưa hiểu lắm! Bạn nói rõ hơn tên giày hoặc nhu cầu (giá, còn hàng không) để mình hỗ trợ nha! 😥"
    })


def about(request):
    return render(request, 'core/about.html')


def admin_dashboard_data(request):
    # Thống kê trạng thái đơn hàng
    stats = [
        CartOrder.objects.filter(product_status="Đang xử lý").count(),
        CartOrder.objects.filter(paid_status=True).count(),
        CartOrder.objects.filter(product_status="Hủy").count(),
    ]
    
    # Bạn có thể thêm thống kê doanh thu theo tháng tại đây
    # ...
    
    return stats


def redeem_coupon(request, id):
    coupon = Coupon.objects.get(id=id)
    # Lấy profile mới nhất từ DB
    user_profile = Profile.objects.get(user=request.user)

    if user_profile.points >= coupon.points_required:
        # Sử dụng F() để trừ điểm trực tiếp trên Database tránh lỗi đồng bộ
        user_profile.points = F('points') - coupon.points_required
        user_profile.save()
        
        # Tạo bản ghi sở hữu
        UserCoupon.objects.create(user=request.user, coupon=coupon)
        
        # Quan trọng: Refresh lại user_profile để lấy số điểm mới sau khi trừ bằng F() 
        # trước khi hiển thị message (nếu cần)
        user_profile.refresh_from_db()
        
        messages.success(request, f"Đổi thành công! Số dư mới: {user_profile.points} điểm.")
    else:
        messages.error(request, "Bạn không đủ điểm để đổi mã này.")
    
    return redirect('core:account-details')
