def calculate_match_score(product_title, message):
    title_words = product_title.lower().split()
    message_words = message.split()
    
    # Đếm số từ trong tên sản phẩm xuất hiện trong tin nhắn
    score = sum(1 for w in title_words if w in message_words)
    return score


def product_to_dict(product):
    return {
        'id': product.id,
        'title': product.title,
        'price': f'{product.price:,}₫',
        'image': product.image.url if product.image else '',
        'url': product.get_absolute_url(),
        'stock': product.stock
    }
