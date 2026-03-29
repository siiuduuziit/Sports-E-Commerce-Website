import google.generativeai as genai
from django.conf import settings
import json

# Cấu hình API key
genai.configure(api_key=settings.GEMINI_API_KEY)

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config={
        "response_mime_type": "application/json",
        "temperature": 0
    }
)

def ai_understand(message):
    prompt = f"""
Bạn là chatbot chuyên hỗ trợ bán giày và đồ thể thao.
Phân tích câu chat của người dùng và CHỈ TRẢ VỀ JSON.

Câu người dùng: "{message}"

JSON:
{{
  "intent": "price" | "stock" | "similar" | "list" | "unknown",
  "product_name": null hoặc string
}}
"""
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as e:
        print("Gemini error:", e)
        return {"intent": "unknown", "product_name": None}
