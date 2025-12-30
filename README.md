# Жестовый помощник — Веб-приложение для распознавания и изучения русского жестового языка

Полнофункциональное веб-приложение для распознавания, изучения и практики русского жестового языка. Проект включает современный фронтенд на React и высокопроизводительный бэкенд на FastAPI.

## Архитектура проекта

Весь проект состоит из двух независимых компонентов, которые могут запускаться как вместе, так и раздельно, в данном репозитории представлена только backend-часть приложения:

```
└── backend/           # FastAPI бэкенд (Python)
    ├── app/
    │   ├── routers/   # Маршруты API
    │   ├── models/    # SQLAlchemy модели
    │   ├── schemas/   # Pydantic схемы
    │   └── database.py
    ├── Dockerfile
    ├── docker-compose.yml
    └── requirements.txt
```

## Быстрый старт

### Вариант 1: Запуск с Docker Compose (рекомендуется)

Самый простой способ запустить все компоненты одной командой:

```bash
# Клонируйте репозиторий
git clone <your-repo-url>
cd жестовый-помощник

# Запустите все сервисы (фронтенд, бэкенд, база данных)
docker-compose up -d --build

# Проверьте статус сервисов
docker-compose ps

# Просмотр логов бэкенда
docker-compose logs -f backend

# Просмотр логов фронтенда
docker-compose logs -f frontend
```

После запуска откройте в браузере:
- **Фронтенд**: http://localhost:5173
- **Бэкенд API**: http://localhost:8000
- **Документация API**: http://localhost:8000/docs

### Вариант 2: Локальный запуск (разработка)

#### Запуск бэкенда:

```bash
# Перейдите в папку бэкенда
cd backend

# Создайте виртуальное окружение (рекомендуется)
python -m venv venv

# Активируйте виртуальное окружение
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt

# Создайте .env файл на основе .env.example
cp .env.example .env
# Отредактируйте .env, указав свои настройки

# Запустите сервер FastAPI с горячей перезагрузкой
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Запуск фронтенда:

```bash
# Откройте новый терминал
cd frontend

# Установите зависимости (если еще не установлены)
npm install

# Запустите сервер разработки
npm run dev
```

## Документация API

### 1. **Swagger UI (интерактивная документация)**
**Доступно по адресу:** http://localhost:8000/docs

**Возможности:**
- Просмотр всех эндпоинтов API
- Интерактивное тестирование (кнопка "Try it out")
- Автоматическая генерация примеров запросов
- Валидация данных в реальном времени
- Визуализация JSON-схем

### 2. **ReDoc (альтернативный интерфейс)**
**Доступно по адресу:** http://localhost:8000/redoc

**Преимущества:**
- Чистый, минималистичный дизайн
- Улучшенная читаемость документации
- Удобная навигация по разделам
- Автоматическая группировка эндпоинтов

### 3. **OpenAPI Specification (JSON)**
**Доступно по адресу:** http://localhost:8000/openapi.json

**Использование спецификации:**
```bash
# Скачайте спецификацию для внешних инструментов
curl http://localhost:8000/openapi.json -o openapi-spec.json

# Импорт в Postman
# 1. Откройте Postman
# 2. Import → Link → Вставьте URL: http://localhost:8000/openapi.json
# 3. Автоматически создастся коллекция со всеми запросами

# Генерация клиентского кода
npx @openapitools/openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g typescript-axios \
  -o ./src/api-client
```

## Аутентификация и авторизация

Система использует JWT (JSON Web Tokens) для безопасной аутентификации.

### Полный flow работы:

1. **Регистрация пользователя** → создание аккаунта с подтверждением email
2. **Подтверждение email** → переход по ссылке из письма
3. **Вход в систему** → получение пары токенов (access + refresh)
4. **Доступ к защищенным ресурсам** → использование access токена
5. **Обновление токенов** → использование refresh токена при истечении срока

### Примеры запросов:

#### Регистрация:
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "newuser",
    "password": "SecurePass123!"
  }'
```

**Ответ:**
```json
{
  "message": "User registered successfully",
  "email": "user@example.com"
}
```

#### Вход в систему:
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=SecurePass123!"
```

**Ответ:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Доступ к защищенному эндпоинту:
```bash
curl -X GET "http://localhost:8000/users/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## Основные эндпоинты API

### Аутентификация

| Метод | Эндпоинт | Описание | Требуется токен |
|-------|----------|----------|-----------------|
| `POST` | `/auth/register` | Регистрация нового пользователя | ❌ |
| `POST` | `/auth/login` | Вход в систему, получение JWT | ❌ |
| `POST` | `/auth/refresh` | Обновление access токена | ❌ (нужен refresh token) |
| `POST` | `/auth/verify-email/{token}` | Подтверждение email | ❌ |
| `POST` | `/auth/forgot-password` | Запрос на сброс пароля | ❌ |
| `POST` | `/auth/reset-password` | Сброс пароля с токеном | ❌ |

### Пользователи

| Метод | Эндпоинт | Описание | Требуется токен |
|-------|----------|----------|-----------------|
| `GET` | `/users/me` | Получение данных текущего пользователя | ✅ |
| `PUT` | `/users/me` | Обновление профиля пользователя | ✅ |

### Системные

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| `GET` | `/` | Проверка работы API |
| `GET` | `/health` | Проверка здоровья сервиса |

## Тестирование API

### С использованием Swagger UI

1. Откройте http://localhost:8000/docs
2. Найдите нужный эндпоинт (например, `POST /auth/register`)
3. Нажмите кнопку **"Try it out"**
4. Заполните JSON данные:
```json
{
  "email": "test@example.com",
  "username": "testuser",
  "password": "Test123!"
}
```
5. Нажмите **"Execute"** для отправки запроса
6. Изучите ответ и код статуса

### С использованием Python скрипта

Создайте файл `test_api.py`:

```python
import requests
import json
from typing import Dict, Optional

class SignLanguageAPIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.access_token: Optional[str] = None
    
    def register(self, email: str, username: str, password: str) -> Dict:
        """Регистрация нового пользователя"""
        url = f"{self.base_url}/auth/register"
        data = {
            "email": email,
            "username": username,
            "password": password
        }
        response = requests.post(url, json=data)
        return response.json()
    
    def login(self, email: str, password: str) -> Dict:
        """Вход в систему"""
        url = f"{self.base_url}/auth/login"
        data = {
            "username": email,
            "password": password
        }
        response = requests.post(url, data=data)
        if response.status_code == 200:
            self.access_token = response.json()["access_token"]
        return response.json()
    
    def get_current_user(self) -> Dict:
        """Получение данных текущего пользователя"""
        if not self.access_token:
            raise ValueError("Необходимо сначала войти в систему")
        
        url = f"{self.base_url}/users/me"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(url, headers=headers)
        return response.json()
    
    def verify_health(self) -> bool:
        """Проверка здоровья сервиса"""
        response = requests.get(f"{self.base_url}/health")
        return response.status_code == 200

# Пример использования
if __name__ == "__main__":
    client = SignLanguageAPIClient()
    
    # Тест здоровья
    print("Проверка здоровья API:", "✅" if client.verify_health() else "❌")
    
    # Регистрация
    print("\n1. Регистрация пользователя...")
    reg_result = client.register(
        email="demo@example.com",
        username="demo_user",
        password="DemoPass123!"
    )
    print(f"   Результат: {reg_result}")
    
    # Вход
    print("\n2. Вход в систему...")
    login_result = client.login("demo@example.com", "DemoPass123!")
    print(f"   Токен получен: {'✅' if 'access_token' in login_result else '❌'}")
    
    # Получение данных пользователя
    print("\n3. Получение данных пользователя...")
    user_data = client.get_current_user()
    print(f"   Данные пользователя: {json.dumps(user_data, indent=2, ensure_ascii=False)}")
```

### С использованием curl (командная строка)

```bash
#!/bin/bash
# test_api.sh - Скрипт для тестирования API

BASE_URL="http://localhost:8000"

echo "=== Тестирование API Жестового помощника ==="

# 1. Проверка здоровья
echo -e "\n1. Проверка здоровья сервиса:"
curl -s "$BASE_URL/health" | jq .

# 2. Регистрация пользователя
echo -e "\n2. Регистрация тестового пользователя:"
REG_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "api_test@example.com",
    "username": "api_tester",
    "password": "TestAPI123!"
  }')
echo "$REG_RESPONSE" | jq .

# 3. Вход в систему
echo -e "\n3. Вход в систему и получение токена:"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=api_test@example.com&password=TestAPI123!")
ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')
echo "Токен: ${ACCESS_TOKEN:0:50}..."

# 4. Доступ к защищенному эндпоинту
echo -e "\n4. Получение данных пользователя:"
curl -s -X GET "$BASE_URL/users/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq .

echo -e "\n=== Тестирование завершено ==="
```

## Конфигурация

### Файл .env

Создайте файл `.env` в папке `backend` на основе `.env.example`:

```env
# ===== БАЗА ДАННЫХ =====
DATABASE_URL=postgresql://postgres:password@postgres:5432/sign_language_db
DATABASE_URL_ASYNC=postgresql+asyncpg://postgres:password@postgres:5432/sign_language_db

# ===== JWT АУТЕНТИФИКАЦИЯ =====
SECRET_KEY=your-super-secret-key-minimum-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ===== EMAIL (SMTP) =====
SMTP_HOST=sandbox.smtp.mailtrap.io
SMTP_PORT=2525
SMTP_USER=your-mailtrap-username
SMTP_PASSWORD=your-mailtrap-password
EMAIL_FROM=noreply@signhelper.ru

# ===== CORS И ФРОНТЕНД =====
FRONTEND_URL=http://localhost:5173

# ===== РЕЖИМ РАЗРАБОТКИ =====
DEBUG=True
```

### Docker Compose

Файл `docker-compose.yml` определяет три сервиса:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: sign_language_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/sign_language_db
      - DATABASE_URL_ASYNC=postgresql+asyncpg://postgres:password@postgres:5432/sign_language_db
    volumes:
      - ./backend:/app
    depends_on:
      - postgres
  
  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules

volumes:
  postgres_data:
```

## Устранение неполадок

### Общие проблемы и решения

| Проблема | Причина | Решение |
|----------|---------|---------|
| **Сервер не запускается** | Порт 8000 уже занят | `netstat -ano \| findstr :8000` и освободите порт |
| **Ошибка импорта модулей** | Не установлены зависимости | `pip install -r requirements.txt` |
| **Нет подключения к БД** | PostgreSQL не запущен | `docker-compose start postgres` |
| **CORS ошибки в браузере** | Неправильный FRONTEND_URL | Проверьте значение FRONTEND_URL в .env |
| **Ошибка ModuleNotFoundError** | Нет драйвера asyncpg | Добавьте `asyncpg` в requirements.txt |
| **Пустой ответ от сервера** | Ошибка в коде приложения | Проверьте логи: `docker-compose logs backend` |

### Команды для диагностики

```bash
# Проверка запущенных контейнеров
docker-compose ps

# Просмотр логов бэкенда
docker-compose logs -f backend

# Проверка подключения к базе данных
docker-compose exec postgres psql -U postgres -d sign_language_db -c "\dt"

# Тестирование API из контейнера
docker-compose exec backend curl http://localhost:8000/health

# Пересборка и запуск
docker-compose down && docker-compose up -d --build

# Очистка томов Docker (полный сброс)
docker-compose down -v
```

## Вклад в проект

Мы приветствуем вклад в проект! Вот как вы можете помочь:

1. **Сообщить об ошибке**
   - Откройте Issue с описанием проблемы
   - Укажите шаги для воспроизведения
   - Приложите логи и скриншоты если возможно

2. **Предложить новую функцию**
   - Опишите предлагаемую функцию
   - Объясните, как она улучшит проект
   - По возможности приложите прототип
