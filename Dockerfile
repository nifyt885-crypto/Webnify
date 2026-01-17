# Используем легкий образ Python
FROM python:3.11-alpine

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY . .

# Создаем пользователя для безопасности
RUN adduser -D -u 1000 botuser
USER botuser

# Запускаем бота
CMD ["python", "app.py"]
