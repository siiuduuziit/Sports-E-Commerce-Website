from core.views import ChatbotLog


def save_chat_log(message, product=None):
    ChatbotLog.objects.create(
        message=message,
        matched_product=product
    )