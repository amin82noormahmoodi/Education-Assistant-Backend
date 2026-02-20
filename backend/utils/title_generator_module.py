import os
import json
from langchain_groq import ChatGroq

with open(r"./config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

llm_model = config["GROQ_LLM_MODEL"]
api_key = config["GROQ_API_KEY"]

llm = ChatGroq(model=llm_model, api_key=api_key)

def generate_title(message: list[dict]) -> str:
    prompt = f"""
بر اساس این پیام کاربر یک عنوان مناسب  و کوتاه برای چت ایجاد بکن.
در خروجی فقط عنوان را برگردان.
خروجی تو به همان زبان ورودی کاربر باشد.
پیام کاربر: {message}
    """
    response = llm.invoke(prompt)
    return response.content