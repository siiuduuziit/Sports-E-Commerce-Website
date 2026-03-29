from core.models import Product


def get_best_product(products, message, calculate_match_score):
    best_product = None
    highest_score = 0

    for p in products:
        score = calculate_match_score(p.title, message)
        if score > highest_score and score >= 2:
            highest_score = score
            best_product = p

    return best_product


def get_similar_products(product, limit=3):
    qs = Product.objects.filter(
        category=product.category
    ).exclude(pid=product.pid)

    if hasattr(product, 'title') and product.title:
        qs = qs.filter(title=product.title)

    return qs[:limit]
