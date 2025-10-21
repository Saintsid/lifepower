# Сайт "Сила природы" - Оздоровительный центр

Статический сайт для оздоровительного центра в Таганроге.

## Структура проекта

```
sila-prirody/
├── index.html          # Главная страница
├── services.html       # Страница услуг
├── about.html          # О центре
├── contacts.html       # Контакты
├── css/
│   └── style.css       # Основные стили
├── js/
│   └── form.js         # Обработка контактной формы
└── images/             # Директория для изображений (пустая)
```

## Быстрый деплой на Nginx

### 1. Копирование файлов на сервер

```bash
scp -r sila-prirody/ user@your-server:/var/www/
```

### 2. Настройка Nginx

Создайте конфигурацию:

```bash
nano /etc/nginx/sites-available/sila-prirody
```

Добавьте:

```nginx
server {
    listen 80;
    server_name your-domain.ru www.your-domain.ru;
    
    root /var/www/sila-prirody;
    index index.html;
    
    location / {
        try_files $uri $uri/ =404;
    }
    
    # Кеширование статики
    location ~* \.(css|js|jpg|jpeg|png|gif|ico|svg|woff|woff2)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Gzip сжатие
    gzip on;
    gzip_types text/css application/javascript text/html;
}
```

Активируйте конфигурацию:

```bash
ln -s /etc/nginx/sites-available/sila-prirody /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### 3. Установка SSL (Let's Encrypt)

```bash
certbot --nginx -d your-domain.ru -d www.your-domain.ru
```

## Альтернатива: Docker

Создайте `Dockerfile`:

```dockerfile
FROM nginx:alpine
COPY . /usr/share/nginx/html
EXPOSE 80
```

Запустите:

```bash
docker build -t sila-prirody .
docker run -d -p 80:80 sila-prirody
```

## Что нужно доделать

1. **Контактная форма**: Сейчас форма только показывает alert. Нужно:
   - Настроить бэкенд для приёма заявок (PHP/Python/Node.js)
   - Или интегрировать с сервисами (Formspree, EmailJS)

2. **Изображения**: Добавить фотографии в папку `images/`

3. **Карта**: Добавить Яндекс.Карты на страницу контактов

4. **SEO**: 
   - Создать robots.txt
   - Добавить sitemap.xml
   - Настроить Google Analytics / Яндекс.Метрику

5. **Телефон и email**: Заменить на реальные контакты в `contacts.html`

## Технические характеристики

- Чистый HTML5/CSS3/JS
- Адаптивный дизайн (mobile-first)
- Размер: ~30 KB (без изображений)
- Время загрузки: <1 сек
- SEO-оптимизирован

## Поддержка браузеров

- Chrome/Edge: последние 2 версии
- Firefox: последние 2 версии
- Safari: последние 2 версии
- Mobile: iOS 12+, Android 8+
