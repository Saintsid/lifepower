-- SQL скрипт для создания первого администратора
-- Используйте этот скрипт после запуска контейнеров

-- Подключитесь к БД командой:
-- docker-compose exec postgres psql -U lifepower lifepower_db

-- Затем выполните эту команду:

INSERT INTO users (email, password_hash, name, phone, role, created_at) 
VALUES (
    'admin@lifepower.su',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ztP.vKJ5pQUa',
    'Администратор',
    '+7 (928) 190-50-01',
    'admin',
    NOW()
);

-- Учетные данные для входа:
-- Email: admin@lifepower.su
-- Пароль: admin123

-- ВАЖНО: После первого входа в продакшене смените пароль!

