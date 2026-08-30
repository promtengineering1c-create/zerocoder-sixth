"""
Асинхронный перевод текста через бесплатный web-API Google.
"""
import asyncio

from googletrans import Translator

translator = Translator()

def _sync_translate(text: str) -> str:
    result = translator.translate(text, dest='en')
    return result.text

async def translate_text(text: str) -> str:
    try:
        return await asyncio.to_thread(_sync_translate, text)
    except Exception as e:  # noqa: BLE001
        return f"Ошибка перевода: {e}"