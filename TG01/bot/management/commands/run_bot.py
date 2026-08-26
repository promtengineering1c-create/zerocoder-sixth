import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from django.conf import settings
from django.core.management.base import BaseCommand
from weather_api.client import close_weather_session

from bot.handlers import router

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Запуск Telegram бота"
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Запуск бота..."))

        try:
            asyncio.run(self._run_bot())
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Бот остановлен пользователем."))

    async def _run_bot(self):
        bot = Bot(token=settings.BOT.token)
        storage = RedisStorage.from_url(settings.REDIS.url)
        dp = Dispatcher(storage=storage)

        dp.include_router(router)

        dp.shutdown.register(on_shutdown)

        await bot.delete_webhook(drop_pending_updates=True)

        logger.info("Бот запущен.")
        
        await dp.start_polling(bot)

async def on_shutdown(bot: Bot) -> None:
    logger.info('Завершение работы бота')

    await close_weather_session()

    logger.info('Закрытие сессии бота')