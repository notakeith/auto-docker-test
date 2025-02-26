import subprocess
import os
import requests
import time
from datetime import datetime
import docker

# Настройки
REPO_DIR = "/app"
GITHUB_REPO = "https://api.github.com/repos/ваш-username/ваш-репозиторий/commits"
POLL_INTERVAL = 300  # Интервал проверки в секундах (например, 300 = 5 минут)
DOCKER_IMAGE_NAME = "my-app"  # Имя образа
CONTAINER_NAME = "my-app-container"  # Имя контейнера

# Функция для получения последнего коммита из GitHub
def get_latest_commit():
    response = requests.get(GITHUB_REPO)
    if response.status_code == 200:
        commits = response.json()
        return commits[0]['sha']  # Хэш последнего коммита
    else:
        print(f"Ошибка при запросе к GitHub: {response.status_code}")
        return None

# Функция для получения текущего коммита в локальном репозитории
def get_local_commit():
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO_DIR, capture_output=True, text=True)
    return result.stdout.strip()

# Функция для перезапуска контейнера
def restart_container():
    client = docker.from_env()
    try:
        # Останавливаем и удаляем старый контейнер
        container = client.containers.get(CONTAINER_NAME)
        container.stop()
        container.remove()
    except docker.errors.NotFound:
        print("Контейнер не найден.")

    # Собираем новый образ
    client.images.build(path=REPO_DIR, tag=DOCKER_IMAGE_NAME)

    # Запускаем новый контейнер
    client.containers.run(
        DOCKER_IMAGE_NAME,
        name=CONTAINER_NAME,
        detach=True,
        restart_policy={"Name": "always"}
    )

# Основная логика
def main():
    while True:
        print(f"[{datetime.now()}] Проверка обновлений...")

        # Удаляем конфликтующие файлы
        conflict_files = ["Dockerfile", "docker-compose.yml", "poll_github.py", "requirements.txt"]
        for file in conflict_files:
            if os.path.exists(file):
                os.remove(file)

        # Получаем последний коммит из GitHub
        latest_commit = get_latest_commit()
        if not latest_commit:
            time.sleep(POLL_INTERVAL)
            continue

        # Получаем текущий коммит в локальном репозитории
        local_commit = get_local_commit()

        # Если коммиты отличаются, обновляем репозиторий и перезапускаем контейнер
        if latest_commit != local_commit:
            print("Обнаружен новый коммит. Обновление репозитория...")

            # Обновляем репозиторий
            subprocess.run(["git", "pull"], cwd=REPO_DIR)

            # Перезапускаем контейнер
            print("Перезапуск контейнера...")
            restart_container()

            print("Обновление завершено.")
        else:
            print("Изменений нет.")

        # Ждем перед следующей проверкой
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()