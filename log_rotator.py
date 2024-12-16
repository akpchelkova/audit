import os
import shutil
import time

LOG_FILE = '/home/akpchelkova/audi/event_log.json'
ARCHIVE_DIR = '/home/akpchelkova/audi/log_archive/'
MAX_SIZE = 10 * 1024 * 1024  # 10MB, например

def rotate_logs():
    # Проверяем размер лог-файла
    if os.path.getsize(LOG_FILE) >= MAX_SIZE:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        archive_name = f"{ARCHIVE_DIR}log_{timestamp}.log"
        
        # Архивируем текущий лог
        shutil.move(LOG_FILE, archive_name)
        
        # Создаем новый пустой лог файл
        with open(LOG_FILE, 'w') as f:
            pass
        print(f"Лог файл ротацирован: {archive_name}")

# Вызов функции
rotate_logs()
