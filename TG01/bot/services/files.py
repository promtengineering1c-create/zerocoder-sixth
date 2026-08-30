from aiogram import Bot
from aiogram.types import Message
from config.settings.base import FILES

FILES.img_dir.mkdir(parents=True, exist_ok=True)
FILES.voice_dir.mkdir(parents=True, exist_ok=True)

async def save_user_photo(message: Message, bot: Bot) -> str:
    photo = message.photo[-1]
    file_path = FILES.img_dir / f"{photo.file_id}.jpg"
    
    await bot.download(photo, destination=file_path)
    return str(file_path)