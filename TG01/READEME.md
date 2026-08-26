# Базовая архитектура проекта Django (Production-ready фундамент)

## 1. Конфигурация и окружение
*   **Модульные настройки:** Оригинальный `settings.py` удален. Создан пакет `config/settings/`.
    *   `base.py` — ядро, содержит общие настройки для всех сред.
    *   `local.py` — настройки для разработки (`DEBUG = True`, локальные хосты).
    *   меняем путь к настройкам в файлах 'manage.py', 'asgi.py', 'wsgi.py'
*   **Переменные окружения:** Интегрирован `django-environ`. Секреты (`SECRET_KEY`, доступы к БД) вынесены в файл `.env`.
*   **Диспетчер:** В `manage.py` переменная окружения переопределена на запуск с `config.settings.local`.

## 2. Инфраструктура путей и локализация
*   **Шаблоны:** Установлен глобальный поиск шаблонов в корне проекта (`BASE_DIR / 'templates'`).
*   **Статика и медиа:** Настроены `STATIC_URL`, `STATICFILES_DIRS`, а также `STATIC_ROOT` для сборки на продакшене и `MEDIA_ROOT` для пользовательских файлов.
*   **Локализация:** Включен русский язык (`ru-ru`) и корректный часовой пояс (`Asia/Yekaterinburg`).

## 3. База данных и безопасность
*   **Подключение:** База инициализируется через `env.db()`, по умолчанию (если нет `.env` переменной) разворачивается `db.sqlite3`.
*   **Первичные ключи:** Задан индустриальный стандарт `BigAutoField`.
*   **Пароли:** Подключены встроенные валидаторы сложности паролей.

## 4. Бизнес-ядро и кастомная модель пользователя
*   **Приложение:** Создано и зарегистрировано главное приложение `core`.
*   **Custom User Model:** В `core.models` создана модель `User` (наследуется от `AbstractUser`). В настройках жестко прописано `AUTH_USER_MODEL = 'core.User'`.
*   **Админка:** Наша кастомная модель выведена во встроенную панель управления с сохранением логики `UserAdmin`.

## 5. Автоматизация (DevOps)
*   **Management Command:** Написан идемпотентный скрипт `core/management/commands/init_project.py` для автоматического создания суперпользователя на основе данных из окружения.


rm -r .venv
python -m pip cache purge
python -m venv venv.
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

Remove-Item -Recurse -Force .venv -ErrorAction SilentlyContinue; python -m pip cache purge; python -m venv .venv; .venv\Scripts\python -m pip install --upgrade pip; .venv\Scripts\python -m pip install -r requirements.txt


django-admin startproject <my_project> .
django-admin startapp <my_app>

python manage.py makemigrations <my_app>
python manage.py migrate

python manage.py init_project

python manage.py runserver