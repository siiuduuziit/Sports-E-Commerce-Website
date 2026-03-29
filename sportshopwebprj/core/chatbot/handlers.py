from django.http import JsonResponse
from .services import get_similar_products
from .constants import *
from .utils import product_to_dict

def handle_price(message, product):
    return JsonResponse({
        "type": "text",
        "data": f"Giá của **{product['title']}** là {product['price']} nha 💰"
    })


def handle_stock(message, product, stock):
    if stock > 0:
        msg = f"Sản phẩm **{product['title']}** còn hàng nha 👍 (SL: {stock})"
    else:
        msg = f"Sản phẩm **{product['title']}** hiện đang hết hàng, bạn có muốn xem thử mẫu tương tự không? 😥"

    return JsonResponse({
        "type": "text",
        "data": msg
    })


def handle_similar(product):
    similar_products = get_similar_products(product)

    if not similar_products:
        return JsonResponse({
            "type": "text",
            "data": "Hiện tại mình chưa có mẫu tương tự phù hợp 😥"
        })

    return JsonResponse({
        "type": "products",
        "data": [product_to_dict(p) for p in similar_products],  # ✅ FIX
        "message": "Mình gợi ý vài mẫu tương tự nè 👟"
    })
