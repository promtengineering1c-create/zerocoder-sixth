import asyncio
import logging
import platform
import socket
import subprocess
import sys
import time

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
        self._ensure_infrastructure()
        self.stdout.write(self.style.SUCCESS("Запуск бота..."))

        try:
            asyncio.run(self._run_bot())
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Бот остановлен пользователем."))

    def _ensure_infrastructure(self):
        self.stdout.write("Проверка инфраструктуры")

        if not self._is_docker_running():
            self.stdout.write(self.style.WARNING("Docker не запущен. Попытка автоматического старта..."))
            self._start_docker_daemon()
            
            if not self._wait_for_docker(timeout=60):
                self.stdout.write(self.style.ERROR(
                    "Не удалось дождаться запуска Docker. \n"
                    "Запустите Docker вручную и попробуйте снова."
                ))
                sys.exit(1)
            self.stdout.write(self.style.SUCCESS("Docker успешно запущен."))

        self.stdout.write("Проверка контейнера Redis...")

        try:
            subprocess.run(
            ["docker", "compose", "up", "-d", "redis"],
            check=True,
            capture_output=True,
            text=True
            )

            self.stdout.write("Контейнер запущен. Ожидание готовности порта 6379...")
            
            # Внедряем жесткую проверку доступности порта
            if self._wait_for_port():
                self.stdout.write(self.style.SUCCESS("Инфраструктура полностью готова: Redis принимает соединения."))
            else:
                self.stdout.write(self.style.ERROR(
                    "Контейнер Redis запущен, но порт 6379 не отвечает.\n"
                    "Возможно, база данных повреждена или порт занят другим приложением."
                ))
                sys.exit(1)

            self.stdout.write(self.style.SUCCESS("Инфраструктура готова"))
        except subprocess.CalledProcessError as e:
            self.stdout.write(self.style.ERROR(f"Ошибка при запуске инфраструктуры: {e.stderr}"))
            sys.exit(1)

    def _is_docker_running(self) -> bool:
        """Проверяет, отвечает ли демон Docker (без учета контейнеров)."""
        try:
            # Команда docker info работает только если демон жив
            subprocess.run(
                ["docker", "info"], 
                check=True, capture_output=True, timeout=5
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _start_docker_daemon(self):
        """Пытается запустить Docker в зависимости от ОС."""
        current_os = platform.system()
        
        try:
            if current_os == "Windows":
                # Запуск Docker Desktop на Windows
                subprocess.Popen(["C:\\Users\\Тимофей\\AppData\\Local\\Programs\\DockerDesktop\\Docker Desktop.exe"])
            elif current_os == "Darwin": # macOS
                subprocess.Popen(["open", "-a", "Docker"])
            elif current_os == "Linux":
                # На Linux это может потребовать sudo, что сломает автоматику,
                # но пробуем мягкий старт системной службы
                subprocess.run(["systemctl", "start", "docker"], check=False)
            else:
                self.stdout.write(self.style.WARNING(f"Автозапуск Docker не поддерживается для ОС {current_os}"))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR("Исполняемый файл Docker не найден по стандартному пути."))
            sys.exit(1)

    def _wait_for_docker(self, timeout: int = 60) -> bool:
        """Ждет инициализации демона Docker."""
        self.stdout.write("Ожидание инициализации ядра Docker (это может занять до минуты)...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self._is_docker_running():
                return True
            time.sleep(2)
            self.stdout.write(".", ending="")
            self.stdout.flush()
            
        self.stdout.write("")
        return False
    async def _run_bot(self):
        bot = Bot(token=settings.BOT.token)
        storage = RedisStorage.from_url(settings.REDIS.url)
        dp = Dispatcher(storage=storage)

        dp.include_router(router)

        dp.shutdown.register(on_shutdown)

        await bot.delete_webhook(drop_pending_updates=True)

        logger.info("Бот запущен.")
        
        await dp.start_polling(bot)

    def _wait_for_port(self, host="127.0.0.1", port=6379, timeout_sec=15) -> bool:
        """
        Пытается установить TCP-соединение с указанным хостом и портом.
        Возвращает True, если порт открыт, и False, если время ожидания вышло.
        """
        start_time = time.time()
        while time.time() - start_time < timeout_sec:
            try:
                # Создаем сокет и пытаемся подключиться. 
                # Таймаут на само подключение — 1 секунда, чтобы не зависать надолго.
                with socket.create_connection((host, port), timeout=1):
                    return True
            except (ConnectionRefusedError, OSError, TimeoutError):
                # Порт еще закрыт или контейнер не готов, ждем...
                time.sleep(0.5)
        return False
async def on_shutdown(bot: Bot) -> None:
    logger.info('Завершение работы бота')

    await close_weather_session()

    logger.info('Закрытие сессии бота')