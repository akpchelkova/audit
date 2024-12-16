import os
import json
import time
import psutil
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from concurrent.futures import ThreadPoolExecutor


# Константы
EVENT_LOG_FILE = "event_log.json"  # Общий журнал событий



# Хранилище последних событий для файлов
recent_events = set()


# Функции для логирования событий

def is_excluded_path(path):
    """Проверяет, находится ли путь внутри одной из исключённых директорий"""
    abs_path = os.path.abspath(path)
    for excluded_dir in EXCLUDED_DIRS:
        excluded_abs_path = os.path.abspath(excluded_dir)
        if abs_path.startswith(excluded_abs_path):
            return True
    return False


def log_event(source, event_type, details):
    """Логирует события в общий файл"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "source": source,
        "event_type": event_type,
        **details
    }
    
    with open(EVENT_LOG_FILE, "a") as log:
        log.write(json.dumps(log_entry) + "\n")
    print(f"Logged {source} event: {log_entry}")


def log_file_event(event_type, src_path, dest_path=None):
    """Логирует события файловой системы"""
    if is_excluded_path(src_path):
        return

    event_details = {
        "src_path": src_path,
        "dest_path": dest_path
    }
    log_event("file", event_type, event_details)


def log_network_event(levelname, local_address, remote_address, status):
    """Логирует сетевые события"""
    event_details = {
        "local_address": local_address,
        "remote_address": remote_address,
        "status": status
    }
    log_event("network", levelname, event_details)


def log_process_event(event_type, process_info):
    """Логирует процессы"""
    event_details = {
        "pid": process_info.get("pid"),
        "name": process_info.get("name"),
        "user": process_info.get("username")
    }
    log_event("process", event_type, event_details)


# Функции для мониторинга

def start_file_monitor(directory_to_watch):
    """Мониторинг файловой системы"""
    class FileMonitorHandler(FileSystemEventHandler):
        def on_created(self, event):
            log_file_event("FILE_CREATED", event.src_path)

        def on_deleted(self, event):
            log_file_event("FILE_DELETED", event.src_path)

        def on_modified(self, event):
            log_file_event("FILE_MODIFIED", event.src_path)

        def on_moved(self, event):
            log_file_event("FILE_MOVED", event.src_path, event.dest_path)

    event_handler = FileMonitorHandler()
    observer = Observer()
    observer.schedule(event_handler, directory_to_watch, recursive=True)
    observer.start()
    print(f"Monitoring started on directory: {directory_to_watch}")

    try:
        while True:
            time.sleep(1)  # Задержка для снижения нагрузки на CPU
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def monitor_network():
    """Мониторинг сетевых соединений"""
    prev_connections = psutil.net_connections(kind='inet')
    while True:
        time.sleep(1)
        current_connections = psutil.net_connections(kind='inet')

        new_connections = [conn for conn in current_connections if conn not in prev_connections]
        for conn in new_connections:
            log_network_event('New connection', str(conn.laddr), str(conn.raddr), conn.status)

        closed_connections = [conn for conn in prev_connections if conn not in current_connections]
        for conn in closed_connections:
            log_network_event('Closed connection', str(conn.laddr), str(conn.raddr), conn.status)

        prev_connections = current_connections


def monitor_processes():
    """Мониторинг процессов"""
    existing_pids = set(psutil.pids())
    while True:
        current_pids = set(psutil.pids())
        new_pids = current_pids - existing_pids
        for pid in new_pids:
            try:
                process = psutil.Process(pid)
                process_info = {
                    "pid": process.pid,
                    "name": process.name(),
                    "username": process.username()
                }
                log_process_event("PROCESS_START", process_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        ended_pids = existing_pids - current_pids
        for pid in ended_pids:
            log_process_event("PROCESS_END", {"pid": pid, "name": "unknown", "username": "unknown"})

        existing_pids = current_pids


# Основной код для параллельного запуска мониторов

if __name__ == "__main__":
    directory = input("Enter the directory to monitor (e.g., /home/user): ").strip()

    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist!")
    else:
        # Создаем пул потоков для параллельного выполнения
        with ThreadPoolExecutor(max_workers=3) as executor:
            executor.submit(start_file_monitor, directory)
            executor.submit(monitor_network)
            executor.submit(monitor_processes)
