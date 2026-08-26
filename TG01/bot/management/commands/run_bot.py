import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from django.conf import settings
from django.core.management.base import BaseCommand

from bot.handlers import router

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Запуск Telegram бота"
    def handle(self, *args, **options):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            )
        self.stdout.write(self.style.SUCCESS("Запуск бота..."))

        try:
            asyncio.run(self._run_bot())
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Бот остановлен пользователем."))

    async def _run_bot(self):
        logger.info("Асинхронный запуск выполнен.")

        bot = Bot(token=settings.BOT.token)

        storage = RedisStorage.from_url(settings.REDIS.url)

        dp = Dispatcher(storage=storage)
        dp.include_router(router)

        self.stdout.write(self.style.SUCCESS('Бот успешно запущен (FSM Redis)'))
        await dp.start_polling(bot)

    