# LifePower - Оздоровительный центр "Сила жизни"

Веб-сайт оздоровительного центра в Таганроге с услугами нутрициологии, гирудотерапии, массажа и wellness-программ.

## Технологии

### Frontend
- HTML5, CSS3, JavaScript
- Раздается через системный Nginx (не в Docker)

### Backend
- FastAPI (Python 3.11)
- PostgreSQL 15
- SQLAlchemy ORM
- Docker для изоляции

### DevOps
- Docker & Docker Compose (только для backend и БД)
- Системный Nginx с SSL (Let's Encrypt)
- GitHub Actions для автоматического деплоя

## Архитектура

```
Сервер (lifepower.su)
│
├── Nginx (системный, порт 80/443)
│   ├── SSL/TLS (Let's Encrypt)
│   ├── Раздает статику: /opt/lifepower/frontend/static/
│   └── Проксирует API: /api/ → http://127.0.0.1:8002/
│
└── Docker Compose
    ├── FastAPI (127.0.0.1:8002)
    └── PostgreSQL (внутренний)
```

## Структура проекта

```
LifePower/
├── frontend/
│   └── static/           # Фронтенд (раздается системным nginx)
│       ├── index.html    # Главная страница
│       ├── services.html # Услуги
│       ├── about.html    # О центре
│       ├── contacts.html # Контакты
│       ├── css/          # Стили
│       ├── js/           # Скрипты
│       └── {css,js,images}/ # Изображения
├── backend/              # Backend API
│   ├── app/
│   │   └── main.py      # FastAPI приложение
│   ├── Dockerfile       # Docker образ backend
│   └── requirements.txt # Python зависимости
├── .github/
│   └── workflows/
│       └── deploy.yml   # CI/CD pipeline
└── docker-compose.yml   # Только FastAPI + PostgreSQL
```

## Локальная разработка

### Предварительные требования
- Docker и Docker Compose
- Git

### Запуск проекта

1. Клонировать репозиторий:
```bash
git clone <repo-url>
cd LifePower
```

2. Запустить контейнеры:
```bash
docker-compose up -d
```

3. Проверить статус:
```bash
docker-compose ps
```

Приложение будет доступно:
- **Backend API**: http://localhost:8002/
- **API Docs**: http://localhost:8002/docs
- **Health Check**: http://localhost:8002/health

**Примечание:** Локально фронтенд нужно открывать напрямую через файлы или настроить локальный веб-сервер.

### Остановка

```bash
docker-compose down
```

## Деплой

Деплой выполняется автоматически через GitHub Actions при пуше в ветки `main` или `master`.

### Необходимые секреты в GitHub

В настройках репозитория (Settings → Secrets and variables → Actions) добавить:

1. `SSH_HOST` - IP-адрес или домен сервера (lifepower.su)
2. `SSH_USERNAME` - имя пользователя SSH
3. `SSH_PRIVATE_KEY` - приватный SSH ключ для доступа к серверу

### Процесс деплоя

1. GitHub Actions копирует файлы на сервер через rsync в `/opt/lifepower/`
2. На сервере выполняется:
   ```bash
   cd /opt/lifepower
   docker-compose down        # Остановка старых контейнеров
   docker-compose build       # Сборка новых образов
   docker-compose up -d       # Запуск в фоне
   docker image prune -f      # Очистка старых образов
   ```
3. Nginx автоматически начинает раздавать обновленные файлы

### Конфигурация Nginx на сервере

Системный Nginx настроен так:
- **Домен**: lifepower.su, www.lifepower.su
- **SSL**: Автоматический редирект HTTP → HTTPS
- **Статика**: `/opt/lifepower/frontend/static/`
- **API**: `/api/*` проксируется на `http://127.0.0.1:8002/`

## API Endpoints

- `GET /` - Информация об API
- `GET /health` - Проверка здоровья сервиса
- `GET /docs` - Swagger UI документация
- `GET /redoc` - ReDoc документация

## Переменные окружения

### PostgreSQL
- `POSTGRES_USER`: lifepower
- `POSTGRES_PASSWORD`: changeme (⚠️ изменить в продакшене!)
- `POSTGRES_DB`: lifepower_db

### Backend
- `DATABASE_URL`: строка подключения к БД

## Безопасность

✅ **Реализовано:**
- SSL/TLS сертификат (Let's Encrypt)
- FastAPI доступен только на localhost (127.0.0.1:8002)
- PostgreSQL изолирован внутри Docker сети

⚠️ **Важно для продакшена:**
1. Изменить пароль PostgreSQL в `docker-compose.yml`
2. Настроить firewall (разрешить только 80, 443, SSH)
3. Регулярные бэкапы базы данных

## Мониторинг

### Проверка логов

```bash
# Docker контейнеры
docker-compose logs -f fastapi
docker-compose logs -f postgres

# Nginx
sudo tail -f /var/log/nginx/lifepower_access.log
sudo tail -f /var/log/nginx/lifepower_error.log
```

### Проверка статуса

```bash
# Контейнеры
docker-compose ps

# Nginx
sudo systemctl status nginx

# Проверка API
curl http://127.0.0.1:8002/health
curl https://lifepower.su/api/health
```

## Обслуживание

### Обновление SSL сертификата

Certbot настроен на автоматическое обновление. Проверка:
```bash
sudo certbot renew --dry-run
```

### Бэкап базы данных

```bash
cd /opt/lifepower
docker-compose exec postgres pg_dump -U lifepower lifepower_db > backup_$(date +%Y%m%d).sql
```

### Восстановление

```bash
docker-compose exec -T postgres psql -U lifepower lifepower_db < backup_20250101.sql
```

## Устранение неполадок

### API не отвечает
```bash
# Проверить контейнеры
docker-compose ps
docker-compose logs fastapi

# Перезапустить
docker-compose restart fastapi
```

### 502 Bad Gateway
- Проверить, запущен ли контейнер FastAPI
- Проверить порт 8002: `netstat -tulpn | grep 8002`
- Проверить конфиг nginx

### База данных недоступна
```bash
docker-compose logs postgres
docker-compose restart postgres
```

## Контакты

- **Сайт**: https://lifepower.su
- **Адрес**: Ростовская область, Таганрог, Смирновский переулок, 10

---

© 2025 Сила жизни. Все права защищены.
