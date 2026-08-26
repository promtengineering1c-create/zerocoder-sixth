from pathlib import Path

import dj_database_url
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class BotSettings(BaseModel):
    token: str

class WeatherSettings(BaseModel):
    api_key: str
    api_url: str = "https://api.openweathermap.org/data/2.5/weather"

class RedisSettings(BaseModel):
    url: str = "redis://127.0.0.1:6379/0"

class EnvironmentSettings(BaseSettings):
    DEBUG: bool = False
    SECRET_KEY: str
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
    ALLOWED_HOSTS: str = "127.0.0.1,localhost"

    TELEGRAM_BOT_TOKEN: str

    OPENWEATHER_API_KEY: str

    REDIS_URL: str = "redis://127.0.0.1:6379/0"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / '.env',
        env_file_encoding='utf-8',
        extra='ignore'
    ) 

    @property
    def bot(self) -> BotSettings:
        return BotSettings(token=self.TELEGRAM_BOT_TOKEN)

    @property
    def weather(self) -> WeatherSettings:
        return WeatherSettings(api_key=self.OPENWEATHER_API_KEY)

    @property
    def redis(self) -> RedisSettings:
        return RedisSettings(url=self.REDIS_URL)

env = EnvironmentSettings()

SECRET_KEY = env.SECRET_KEY
DEBUG = env.DEBUG

ALLOWED_HOSTS = [host.strip() for host in env.ALLOWED_HOSTS.split(',') if host.strip()]

BOT = env.bot
WEATHER = env.weather
REDIS = env.redis

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = []

LOCAL_APPS = [
    # 'core.apps.CoreConfig',
    # 'accounts.apps.AccountsConfig',
    'bot.apps.BotConfig',
    'weather_api.apps.WeatherApiConfig'
]

INSTALLED_APPS = LOCAL_APPS + THIRD_PARTY_APPS + DJANGO_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Сразу учим Django искать HTML-файлы не только внутри приложений, 
        # но и в общей папке templates в корне проекта.
        'DIRS': [BASE_DIR / 'templates'], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# === ИНТЕРФЕЙСЫ СЕРВЕРА ===
WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
# Склад для сборки статики на продакшене (создастся автоматически командой collectstatic)
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Медиа (пользовательские загрузки)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DATABASES = {
    'default': dj_database_url.parse(env.DATABASE_URL)
}

# Стандартная настройка для первичных ключей (ID) моделей
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# === ЛОКАЛИЗАЦИЯ И ВРЕМЯ ===
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Asia/Yekaterinburg'
USE_I18N = True
USE_TZ = True

# AUTH_USER_MODEL = 'core.User'


