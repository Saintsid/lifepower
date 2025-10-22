# 🏗️ Архитектура системы v1.0.0

## 📊 Общая схема

```
┌─────────────────────────────────────────────────────────────┐
│                         Пользователь                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Nginx (Port 443/80)                       │
│                  lifepower.su (SSL/TLS)                      │
└─────────────────────────────────────────────────────────────┘
                              │
            ┌─────────────────┴─────────────────┐
            ▼                                   ▼
┌──────────────────────────┐      ┌──────────────────────────┐
│   Static Files           │      │   FastAPI Backend        │
│   (HTML/CSS/JS)          │      │   (Port 127.0.0.1:8002)  │
│                          │      │                          │
│   - index.html           │      │   API Endpoints:         │
│   - login.html           │      │   - /api/register        │
│   - register.html        │      │   - /api/login           │
│   - client-dashboard.html│      │   - /api/me              │
│   - admin-dashboard.html │      │   - /api/bookings        │
│   - booking.html         │      │   - /api/admin/*         │
│   - privacy.html         │      │                          │
│   - js/auth.js           │      └──────────┬───────────────┘
│   - js/form.js           │                 │
└──────────────────────────┘                 │
                                             ▼
                              ┌──────────────────────────────┐
                              │   PostgreSQL 15              │
                              │   (Port internal:5432)       │
                              │                              │
                              │   Tables:                    │
                              │   - users                    │
                              │   - bookings                 │
                              │                              │
                              │   Volume:                    │
                              │   postgres_data              │
                              └──────────────────────────────┘
```

---

## 🔐 Поток авторизации

```
┌─────────┐                 ┌─────────┐                 ┌──────────┐
│ Browser │                 │ FastAPI │                 │ Database │
└────┬────┘                 └────┬────┘                 └────┬─────┘
     │                           │                           │
     │ 1. POST /api/register     │                           │
     │ {email, password, ...}    │                           │
     │──────────────────────────>│                           │
     │                           │ 2. Hash password (bcrypt) │
     │                           │                           │
     │                           │ 3. INSERT INTO users      │
     │                           │──────────────────────────>│
     │                           │                           │
     │                           │ 4. User created           │
     │                           │<──────────────────────────│
     │                           │                           │
     │ 5. {user data}            │                           │
     │<──────────────────────────│                           │
     │                           │                           │
     │ 6. POST /api/login        │                           │
     │ {email, password}         │                           │
     │──────────────────────────>│                           │
     │                           │ 7. SELECT user            │
     │                           │──────────────────────────>│
     │                           │                           │
     │                           │ 8. User data              │
     │                           │<──────────────────────────│
     │                           │                           │
     │                           │ 9. Verify password        │
     │                           │    (bcrypt)               │
     │                           │                           │
     │                           │ 10. Generate JWT token    │
     │                           │     (30 days expiry)      │
     │                           │                           │
     │ 11. {access_token, user}  │                           │
     │<──────────────────────────│                           │
     │                           │                           │
     │ 12. Store token in        │                           │
     │     localStorage          │                           │
     │                           │                           │
```

---

## 🔄 Поток создания записи

```
┌─────────┐                 ┌─────────┐                 ┌──────────┐
│ Browser │                 │ FastAPI │                 │ Database │
└────┬────┘                 └────┬────┘                 └────┬─────┘
     │                           │                           │
     │ 1. GET /api/me            │                           │
     │    Authorization: Bearer TOKEN                        │
     │──────────────────────────>│                           │
     │                           │ 2. Decode JWT             │
     │                           │    Extract email          │
     │                           │                           │
     │                           │ 3. SELECT user            │
     │                           │──────────────────────────>│
     │                           │                           │
     │                           │ 4. User data              │
     │                           │<──────────────────────────│
     │                           │                           │
     │ 5. {id, email, name, ...} │                           │
     │<──────────────────────────│                           │
     │                           │                           │
     │ 6. Prefill form with      │                           │
     │    user data              │                           │
     │                           │                           │
     │ 7. POST /api/bookings     │                           │
     │    Authorization: Bearer TOKEN                        │
     │    {name, phone, service, ...}                       │
     │──────────────────────────>│                           │
     │                           │ 8. Verify JWT             │
     │                           │    Get user_id            │
     │                           │                           │
     │                           │ 9. INSERT INTO bookings   │
     │                           │    (user_id, ...)         │
     │                           │──────────────────────────>│
     │                           │                           │
     │                           │ 10. Booking created       │
     │                           │<──────────────────────────│
     │                           │                           │
     │ 11. {booking data}        │                           │
     │<──────────────────────────│                           │
     │                           │                           │
```

---

## 👤 Структура данных

### User Model
```python
class User:
    id: int (PK)
    email: str (unique, indexed)
    password_hash: str
    name: str
    phone: str
    role: Enum['client', 'admin']
    created_at: datetime
    
    # Relationship
    bookings: List[Booking]
```

### Booking Model
```python
class Booking:
    id: int (PK)
    user_id: int (FK users.id, nullable)
    name: str
    phone: str
    email: str
    service: str
    message: str
    status: Enum['new', 'contacted', 'confirmed', 'completed', 'cancelled']
    created_at: datetime
    
    # Relationship
    user: User
```

---

## 🔑 JWT Token Structure

```json
{
  "sub": "user@example.com",
  "exp": 1730000000,
  "iat": 1727408000
}
```

**Алгоритм:** HS256  
**Секрет:** Переменная окружения SECRET_KEY  
**Срок действия:** 30 дней (43200 минут)

---

## 🚪 Роли и права доступа

### Client (Клиент)
✅ **Может:**
- Регистрироваться
- Входить в систему
- Создавать записи на консультации
- Просматривать свои записи
- Видеть статусы своих записей

❌ **Не может:**
- Просматривать записи других пользователей
- Изменять статусы записей
- Видеть статистику
- Получать доступ к админ-панели

### Admin (Администратор)
✅ **Может всё, что клиент, плюс:**
- Просматривать все записи
- Изменять статусы любых записей
- Видеть полную статистику
- Получать доступ к админ-панели

---

## 🛡️ Защита эндпоинтов

### Публичные эндпоинты (без авторизации)
```python
GET  /health
POST /api/register
POST /api/login
```

### Защищенные эндпоинты (требуют JWT)
```python
GET  /api/me              # Depends(get_current_user)
POST /api/bookings        # Depends(get_current_user)
GET  /api/bookings        # Depends(get_current_user)
```

### Админ эндпоинты (требуют JWT + роль admin)
```python
GET   /api/admin/bookings       # Depends(require_admin)
PATCH /api/admin/bookings/{id}  # Depends(require_admin)
GET   /api/admin/stats          # Depends(require_admin)
```

---

## 📱 Frontend Routing

### Публичные страницы
```
/                       → index.html
/services.html          → Услуги
/about.html             → О центре
/contacts.html          → Контакты
/booking.html           → Форма записи (может быть с/без авторизации)
/privacy.html           → Политика конфиденциальности
/register.html          → Регистрация
/login.html             → Вход
```

### Защищенные страницы (требуют авторизации)
```
/client-dashboard.html  → ЛК клиента (требует роль: client)
/admin-dashboard.html   → Админ-панель (требует роль: admin)
```

### Логика переадресации
```javascript
// При загрузке дашбордов:
1. Проверить наличие JWT токена в localStorage
2. Если токена нет → редирект на /login.html
3. Если токен есть → запрос GET /api/me
4. Если 401 → редирект на /login.html
5. Если 200 → проверить роль:
   - client на admin-dashboard → редирект на client-dashboard
   - admin на client-dashboard → редирект на admin-dashboard
```

---

## 🗄️ База данных - Связи

```sql
users (1) ←──── (N) bookings

Отношение: Один пользователь может иметь много записей
           Одна запись принадлежит одному пользователю (или NULL)
```

### Создание таблиц
Таблицы создаются автоматически при запуске FastAPI:
```python
Base.metadata.create_all(bind=engine)
```

---

## 🔧 Технический стек

### Backend
- **Framework:** FastAPI 0.104.1
- **Server:** Uvicorn (ASGI)
- **Database:** PostgreSQL 15 Alpine
- **ORM:** SQLAlchemy 2.0.23
- **Auth:** python-jose (JWT)
- **Password:** passlib (bcrypt)
- **Validation:** Pydantic 2.5.0

### Frontend
- **HTML5** - разметка
- **CSS3** - стилизация
- **Vanilla JavaScript** - логика
- **LocalStorage** - хранение JWT токенов
- **Fetch API** - HTTP запросы

### Infrastructure
- **Docker** - контейнеризация
- **Docker Compose** - оркестрация
- **Nginx** - reverse proxy, SSL
- **GitHub Actions** - CI/CD

---

## 🔄 Жизненный цикл запроса

### Пример: Клиент создает запись

```
1. Пользователь открывает /booking.html
   └─> JavaScript: getCurrentUser() → GET /api/me
       └─> Backend: Проверяет JWT → Возвращает данные пользователя
           └─> Frontend: Автозаполняет форму

2. Пользователь заполняет форму и нажимает "Отправить"
   └─> JavaScript: apiRequest('/bookings', {method: 'POST', body: {...}})
       └─> Backend: 
           1. Проверяет JWT токен
           2. Извлекает user_id из токена
           3. Валидирует данные через Pydantic
           4. Создает запись в БД
           5. Возвращает созданную запись
       └─> Frontend: Показывает сообщение успеха

3. Пользователь переходит в личный кабинет
   └─> JavaScript: loadDashboard()
       └─> apiRequest('/bookings') → GET /api/bookings
           └─> Backend:
               1. Проверяет JWT
               2. SELECT bookings WHERE user_id = current_user.id
               3. Возвращает список записей
           └─> Frontend: Рендерит таблицу с записями
```

---

## 🧪 Примеры API запросов

### Регистрация
```bash
curl -X POST https://lifepower.su/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "name": "Иван Иванов",
    "phone": "+7 999 123 45 67"
  }'
```

### Вход
```bash
curl -X POST https://lifepower.su/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

Ответ:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "test@example.com",
    "name": "Иван Иванов",
    "phone": "+7 999 123 45 67",
    "role": "client",
    "created_at": "2025-10-22T10:00:00"
  }
}
```

### Создание записи (с авторизацией)
```bash
curl -X POST https://lifepower.su/api/bookings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "name": "Иван Иванов",
    "phone": "+7 999 123 45 67",
    "email": "test@example.com",
    "service": "nutrition",
    "message": "Хочу записаться на консультацию"
  }'
```

### Получение статистики (только админ)
```bash
curl -X GET https://lifepower.su/api/admin/stats \
  -H "Authorization: Bearer ADMIN_TOKEN_HERE"
```

Ответ:
```json
{
  "total_bookings": 42,
  "new_bookings": 5,
  "confirmed_bookings": 10,
  "completed_bookings": 20,
  "total_users": 15
}
```

---

## 📈 Масштабируемость

### Текущая архитектура
- 1 контейнер FastAPI
- 1 контейнер PostgreSQL
- Nginx на хосте

### Возможности расширения
1. **Горизонтальное масштабирование FastAPI:**
   - Добавить несколько реплик контейнера
   - Load balancing через Nginx

2. **Кеширование:**
   - Redis для сессий
   - Redis для кеширования статистики

3. **Очередь задач:**
   - Celery для асинхронных задач
   - RabbitMQ/Redis в качестве брокера

4. **Мониторинг:**
   - Prometheus для метрик
   - Grafana для визуализации
   - Sentry для отслеживания ошибок

---

## 🔐 Безопасность

### Реализованные меры
✅ Хеширование паролей (bcrypt, cost=12)  
✅ JWT токены с истечением (30 дней)  
✅ CORS настроен  
✅ SQL injection защита (SQLAlchemy ORM)  
✅ XSS защита (escape в HTML)  
✅ HTTPS (SSL/TLS через Nginx)  
✅ Защита админ-эндпоинтов  

### Рекомендации
- [ ] Rate limiting для API
- [ ] CSRF токены для форм
- [ ] Content Security Policy headers
- [ ] Логирование всех авторизационных событий
- [ ] Two-Factor Authentication (2FA)
- [ ] Email верификация при регистрации

---

## 📊 Метрики производительности

### Целевые показатели
- **Время отклика API:** < 200ms
- **Время загрузки страницы:** < 2s
- **Доступность:** > 99.5%
- **Одновременных пользователей:** до 100

### Мониторинг
```bash
# Проверка времени отклика API
curl -w "@curl-format.txt" -o /dev/null -s https://lifepower.su/api/health

# Проверка состояния контейнеров
docker stats

# Проверка использования БД
docker-compose exec postgres psql -U lifepower -c "SELECT pg_size_pretty(pg_database_size('lifepower_db'));"
```

---

_Документация актуальна на: 22 октября 2025_

