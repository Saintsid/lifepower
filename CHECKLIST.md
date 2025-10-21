# ✅ Чеклист перед пушем

## 🎯 Текущая архитектура

```
Сервер lifepower.su
│
├── Nginx (системный) ← УЖЕ НАСТРОЕН
│   ├── Порты: 80 → 443 (SSL)
│   ├── Раздает: /opt/lifepower/frontend/static/
│   └── Проксирует: /api/ → http://127.0.0.1:8002/
│
└── Docker Compose ← БУДЕТ ЗАДЕПЛОЕН
    ├── FastAPI (127.0.0.1:8002)
    └── PostgreSQL (внутренний)
```

## ✅ Что исправлено

- [x] Убран nginx из docker-compose (используется системный)
- [x] FastAPI биндится на 127.0.0.1:8002 (совпадает с nginx)
- [x] Frontend в `/frontend/static/` (путь из nginx конфига)
- [x] Правильная структура backend/app/main.py
- [x] Все зависимости на месте

## 🔍 Проверки перед пушем

### 1. GitHub Secrets
- [ ] `SSH_HOST` установлен (IP или lifepower.su)
- [ ] `SSH_USERNAME` установлен (ваш пользователь)
- [ ] `SSH_PRIVATE_KEY` установлен (приватный SSH ключ)

### 2. На сервере
- [ ] Docker установлен: `docker --version`
- [ ] Docker Compose установлен: `docker-compose --version`
- [ ] Папка существует: `ls /opt/lifepower`
- [ ] Nginx работает: `sudo systemctl status nginx`
- [ ] SSL настроен (есть сертификат)

### 3. Структура проекта (локально)
```
✅ LifePower/
   ✅ frontend/static/         # HTML, CSS, JS
   ✅ backend/app/main.py      # FastAPI
   ✅ backend/Dockerfile       # Сборка backend
   ✅ backend/requirements.txt # Зависимости
   ✅ docker-compose.yml       # FastAPI + PostgreSQL
   ✅ .github/workflows/deploy.yml
```

## 🚀 Что произойдет после пуша

1. ✅ GitHub Actions скопирует файлы через rsync
2. ✅ На сервере выполнится:
   ```bash
   docker-compose down
   docker-compose build
   docker-compose up -d
   ```
3. ✅ FastAPI поднимется на 127.0.0.1:8002
4. ✅ PostgreSQL поднимется внутри Docker
5. ✅ Nginx начнет проксировать на новый backend

## 🌐 Что будет доступно

После успешного деплоя:

| URL | Что откроется |
|-----|---------------|
| https://lifepower.su/ | Главная страница (frontend) |
| https://lifepower.su/services.html | Услуги |
| https://lifepower.su/about.html | О центре |
| https://lifepower.su/contacts.html | Контакты |
| https://lifepower.su/api/ | API (JSON) |
| https://lifepower.su/api/health | Health check |
| https://lifepower.su/api/docs | Swagger UI |

## 🧪 Как проверить после пуша

### 1. GitHub Actions
```
GitHub → Actions → Deploy LifePower
Должен быть зеленый ✅
```

### 2. SSH на сервер
```bash
ssh user@lifepower.su
cd /opt/lifepower

# Проверить контейнеры
docker-compose ps
# Должно быть:
# lifepower_api    Up
# lifepower_db     Up
```

### 3. Проверить API
```bash
curl https://lifepower.su/api/health
# {"status":"ok"}
```

### 4. Открыть в браузере
```
https://lifepower.su/
```

## ⚠️ Важно ПОСЛЕ первого деплоя

1. **Сменить пароль БД:**
   ```bash
   ssh user@server
   cd /opt/lifepower
   nano docker-compose.yml
   # Изменить POSTGRES_PASSWORD: changeme
   docker-compose down
   docker-compose up -d
   ```

2. **Проверить логи:**
   ```bash
   docker-compose logs -f
   ```

## 🎉 Готово к пушу!

Если все пункты выполнены:
```bash
git add .
git commit -m "Configure deployment with system nginx"
git push origin main
```

И наблюдай в GitHub Actions!

---

## 📞 Если что-то пошло не так

1. **GitHub Actions failed** → Смотри логи в Actions
2. **502 Bad Gateway** → `docker-compose logs fastapi`
3. **API не отвечает** → `docker-compose ps` и `netstat -tulpn | grep 8002`
4. **Статика не обновилась** → `sudo nginx -s reload`

## 🔗 Полезные ссылки

- `README.md` - Полная документация проекта
- `DEPLOY.md` - Подробная инструкция по деплою
- `.github/workflows/deploy.yml` - CI/CD конфигурация

---

© 2025 Сила жизни. Оздоровительный центр в Таганроге.

