# Используем базовый образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости для Git и Docker CLI
RUN apt-get update && apt-get install -y git curl

# Устанавливаем Docker CLI
RUN curl -fsSL https://get.docker.com | sh

# Копируем файлы проекта
COPY . .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем библиотеку docker для Python
RUN pip install docker

# Запускаем скрипт при старте контейнера
CMD ["python", "poll_github.py"]