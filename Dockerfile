# Используем базовый образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости для Git и Python
RUN apt-get update && apt-get install -y git

# Копируем файлы проекта
COPY . .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Копируем скрипт для проверки обновлений
COPY poll_github.py /app/poll_github.py

# Запускаем скрипт при старте контейнера
CMD ["python", "poll_github.py"]