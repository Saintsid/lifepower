# Инструкция по деплою LifePower

## 🏗️ Архитектура проекта

### Как это работает:

```
┌─────────────────────────────────────────┐
│  Nginx (системный, порт 80/443)         │
│  - SSL/TLS (Let's Encrypt)              │
│  - Раздает: /opt/lifepower/frontend/static/ │
│  - Проксирует: /api/ → 127.0.0.1:8002  │
└─────────────────────────────────────────┘
              │
              ├─── Статика (HTML/CSS/JS)
              │
              └─── API запросы
                    │
                    ▼
        ┌─────────────────────────┐
        │ Docker Compose          │
        │  ┌───────────────────┐  │
        │  │ FastAPI           │  │
        │  │ 127.0.0.1:8002    │  │
        │  └───────────────────┘  │
        │           │             │
        │  ┌───────────────────┐  │
        │  │ PostgreSQL        │  │
        │  │ (внутренний порт) │  │
        │  └───────────────────┘  │
        └─────────────────────────┘
```

## ✅ Что было исправлено

### Проблемы которые были:
- ❌ Nginx планировался в Docker (конфликт с системным)
- ❌ Порт FastAPI был 127.0.0.1:8002 в docker-compose, но должен был быть внешним
- ❌ Frontend был не в `/frontend/static/`, как ожидает nginx

### Что исправлено:
- ✅ Убран nginx из docker-compose (используется системный)
- ✅ FastAPI биндится на 127.0.0.1:8002 (как в конфиге nginx)
- ✅ Frontend перемещен в `/frontend/static/` (путь из nginx конфига)
- ✅ Только backend + PostgreSQL в Docker

## 🚀 Что произойдет при пуше

1. **GitHub Actions запустится** автоматически
2. **rsync скопирует** все файлы на сервер в `/opt/lifepower/`
3. **На сервере выполнится:**
   ```bash
   cd /opt/lifepower
   docker-compose down        # Остановка старых контейнеров
   docker-compose build       # Сборка backend образа
   docker-compose up -d       # Запуск FastAPI + PostgreSQL
   docker image prune -f      # Очистка
   ```
4. **Nginx автоматически** начнет раздавать обновленные файлы

## 📦 Что будет запущено

| Сервис | Где | Порт | Описание |
|--------|-----|------|----------|
| Nginx | Системный | 80, 443 | Раздает статику + SSL + проксирует API |
| FastAPI | Docker | 127.0.0.1:8002 | Backend API |
| PostgreSQL | Docker | Внутренний | База данных |

## 🌐 Доступ после деплоя

- **Frontend**: https://lifepower.su/
- **Backend API**: https://lifepower.su/api/
- **API Docs**: https://lifepower.su/api/docs
- **Health Check**: https://lifepower.su/api/health

## 🔧 Что должно быть на сервере

### 1. ✅ Системный Nginx с вашим конфигом
```nginx
server {
    listen 443 ssl http2;
    server_name lifepower.su www.lifepower.su;

    root /opt/lifepower/frontend/static;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8002/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # SSL сертификаты и прочее...
}
```

### 2. ✅ Docker и Docker Compose установлены
```bash
docker --version
docker-compose --version
```

### 3. ✅ Папка создана
```bash
ls -la /opt/lifepower
```

### 4. ✅ SSL сертификат настроен (Let's Encrypt)

## 🔐 GitHub Secrets (должны быть настроены)

| Секрет | Описание | Пример |
|--------|----------|--------|
| `SSH_HOST` | IP или домен сервера | `123.45.67.89` или `lifepower.su` |
| `SSH_USERNAME` | Пользователь SSH | `ubuntu` / `root` |
| `SSH_PRIVATE_KEY` | Приватный SSH ключ | `-----BEGIN OPENSSH...` |

## 🧪 Как проверить после деплоя

### 1. GitHub Actions
Смотрим что workflow завершился успешно ✅

### 2. На сервере (через SSH)
```bash
ssh user@lifepower.su
cd /opt/lifepower

# Проверить контейнеры
docker-compose ps

# Должно быть 2 контейнера "Up":
# - lifepower_api (FastAPI)
# - lifepower_db (PostgreSQL)
```

### 3. Проверить логи
```bash
# FastAPI
docker-compose logs -f fastapi

# PostgreSQL
docker-compose logs -f postgres

# Nginx
sudo tail -f /var/log/nginx/lifepower_access.log
```

### 4. Проверить через curl/браузер
```bash
# Health check
curl https://lifepower.su/api/health
# {"status": "ok"}

# Главная страница
curl -I https://lifepower.su/
# 200 OK
```

### 5. Открыть в браузере
- https://lifepower.su/ - должен открыться сайт
- https://lifepower.su/api/docs - Swagger UI

## 🎯 Ожидаемый результат

При правильных секретах и настройках:
- ✅ Workflow завершится успешно (зеленая галочка)
- ✅ На сервере 2 контейнера в статусе "Up"
- ✅ https://lifepower.su/ открывает сайт
- ✅ https://lifepower.su/api/health отвечает `{"status": "ok"}`
- ✅ SSL работает (зеленый замок в браузере)

## ⚠️ Если что-то пошло не так

### Проблема: 502 Bad Gateway на /api/

**Решение:**
```bash
# Проверить что FastAPI запущен
docker-compose ps

# Проверить логи
docker-compose logs fastapi

# Проверить порт 8002
netstat -tulpn | grep 8002
# Должен быть: 127.0.0.1:8002

# Перезапустить
docker-compose restart fastapi
```

### Проблема: Статика не обновилась

**Решение:**
```bash
# Проверить файлы
ls -la /opt/lifepower/frontend/static/

# Очистить кэш nginx
sudo nginx -s reload
```

### Проблема: Database connection error

**Решение:**
```bash
# Проверить PostgreSQL
docker-compose logs postgres

# Перезапустить
docker-compose restart postgres

# Проверить переменные окружения в docker-compose.yml
```

### Проблема: GitHub Actions failed

**Решение:**
1. Смотрим логи в GitHub → Actions
2. Проверяем секреты (SSH_HOST, SSH_USERNAME, SSH_PRIVATE_KEY)
3. Проверяем SSH доступ вручную:
   ```bash
   ssh user@server
   ```

## 🔒 Безопасность

✅ **Что уже настроено:**
- SSL/TLS сертификат
- FastAPI доступен только на localhost
- PostgreSQL изолирован в Docker

⚠️ **Не забыть:**
1. Сменить пароль БД в `docker-compose.yml`:
   ```yaml
   POSTGRES_PASSWORD: changeme  # ← ИЗМЕНИТЬ!
   ```

2. Проверить firewall:
   ```bash
   sudo ufw status
   # Должны быть открыты только: 22, 80, 443
   ```

## 📊 Структура файлов на сервере после деплоя

```
/opt/lifepower/
├── frontend/
│   └── static/              # Nginx раздает отсюда
│       ├── index.html
│       ├── about.html
│       ├── services.html
│       ├── contacts.html
│       ├── css/
│       ├── js/
│       └── {css,js,images}/
├── backend/
│   ├── app/
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml       # Запускает FastAPI + PostgreSQL
└── .github/
```

## 💡 После успешного деплоя

1. ✅ Проверить все страницы сайта
2. ✅ Проверить API endpoints
3. ✅ Настроить мониторинг (опционально)
4. ✅ Настроить автоматические бэкапы БД
5. ✅ Сменить дефолтные пароли!

---

**Готово к деплою!** 🚀

Твой nginx уже настроен, SSL работает, остается только запушить и Docker Compose поднимет backend с БД.

---

© 2025 Сила жизни. Оздоровительный центр в Таганроге.
