# app/middleware/language_middleware.py
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta


class LanguageMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Определяем язык (приоритеты):
        #    - Из куки 'lang' (если пользователь явно выбрал)
        #    - Из заголовка Accept-Language браузера
        #    - По умолчанию 'ru'

        # Пробуем получить из куки
        lang = request.cookies.get('lang')

        if not lang:
            # Пробуем получить из заголовка Accept-Language
            accept_language = request.headers.get('accept-language', '')
            if accept_language:
                # Берем первый язык из заголовка (например, "ru-RU,ru;q=0.9,en-US;q=0.8")
                primary_lang = accept_language.split(',')[0].split('-')[0].lower()
                if primary_lang in ['ru', 'en', 'es']:
                    lang = primary_lang
                else:
                    lang = 'ru'
            else:
                lang = 'ru'

        # Сохраняем язык в state для использования в эндпоинтах
        request.state.lang = lang

        # Обрабатываем запрос
        response = await call_next(request)

        # Если в куках нет языка, устанавливаем дефолтный
        if 'lang' not in request.cookies:
            response.set_cookie(
                key='lang',
                value=lang,
                max_age=365 * 24 * 60 * 60,  # 1 год
                httponly=True,  # Не доступен из JavaScript (опционально)
                samesite='lax'
            )

        # Добавляем заголовок Content-Language для браузера
        response.headers['Content-Language'] = lang

        return response