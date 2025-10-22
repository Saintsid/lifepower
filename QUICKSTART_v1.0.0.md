# 🚀 Быстрый старт v1.0.0

## Что нового?

✅ Система авторизации (JWT)  
✅ Регистрация и вход пользователей  
✅ Личный кабинет клиента  
✅ Админ-панель с управлением заявками  
✅ Статистика для администратора  

---

## 3 шага до запуска

### 1️⃣ Пересоберите контейнеры

```bash
cd /var/www/lifepower.su
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 2️⃣ Создайте администратора

```bash
docker-compose exec postgres psql -U lifepower lifepower_db
```

Выполните в psql:
```sql
INSERT INTO users (email, password_hash, name, phone, role, created_at) 
VALUES ('admin@lifepower.su', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ztP.vKJ5pQUa', 'Администратор', '+7 (928) 190-50-01', 'admin', NOW());
\q
```

### 3️⃣ Проверьте работу

Откройте в браузере:
- **Регистрация:** https://lifepower.su/register.html
- **Вход:** https://lifepower.su/login.html
- **Админ-панель:** https://lifepower.su/admin-dashboard.html

**Учетные данные администратора:**
- Email: `admin@lifepower.su`
- Пароль: `admin123`

⚠️ **ВАЖНО:** Сразу смените пароль после первого входа!

---

## ⚙️ Настройка безопасности (ОБЯЗАТЕЛЬНО!)

### Сгенерируйте SECRET_KEY

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Вставьте результат в `docker-compose.yml`:
```yaml
environment:
  SECRET_KEY: "ваш-сгенерированный-ключ"
```

Перезапустите:
```bash
docker-compose restart fastapi
```

---

## 📚 Полная документация

- **Инструкция по запуску:** `ИНСТРУКЦИЯ_ПО_ЗАПУСКУ.md`
- **Чеклист деплоя:** `DEPLOY_CHECKLIST_v1.0.0.md`
- **Сводка изменений:** `SUMMARY_UPDATE_v1.0.0.md`
- **История версий:** `CHANGELOG.md`

---

## 🆘 Проблемы?

### Контейнеры не запускаются
```bash
docker-compose logs fastapi
docker-compose logs postgres
```

### Не работает авторизация
1. Очистите localStorage в браузере (F12 → Application → Local Storage)
2. Проверьте, что SECRET_KEY установлен
3. Перезапустите контейнеры

### Таблицы не созданы
```bash
docker-compose exec postgres psql -U lifepower lifepower_db -c "\dt"
```

Если таблиц нет:
```bash
docker-compose restart fastapi
```

---

## ✅ Готово!

Теперь у вас:
- ✅ Работающая авторизация
- ✅ Личные кабинеты
- ✅ Админ-панель
- ✅ API для управления заявками

**Следующий шаг:** Протестируйте функционал и смените пароль администратора! 🎉

