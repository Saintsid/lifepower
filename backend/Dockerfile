FROM python:3.11-slim

WORKDIR /app

# Копируем requirements и устанавливаем зависимости
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем приложение
COPY backend/app/ /app/

# Копируем шаблоны Jinja2
COPY backend/templates/ /app/templates/

# Копируем статические файлы
COPY frontend/static/ /app/static/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]