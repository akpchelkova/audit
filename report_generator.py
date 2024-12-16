import os
import json
import matplotlib.pyplot as plt
from datetime import datetime
from collections import defaultdict, Counter


# Функция для загрузки логов из файла
def load_logs(file_path="event_log.json"):
    try:
        with open(file_path, "r") as file:
            logs = [json.loads(line) for line in file.readlines()]
        return logs
    except FileNotFoundError:
        return []


# Функция для фильтрации логов по выбранным критериям
def filter_logs(logs, event_type=None, user=None, source=None, start_time=None, end_time=None):
    filtered_logs = []
    for log in logs:
        timestamp = datetime.fromisoformat(log['timestamp'])

        if event_type and event_type != log['event_type']:
            continue

        if user and user != log.get('user', ''):
            continue

        if source and source != log.get('source', ''):
            continue

        if start_time and timestamp < start_time:
            continue

        if end_time and timestamp > end_time:
            continue

        filtered_logs.append(log)

    return filtered_logs


# Генерация статистики по типам событий
def generate_event_type_stats(logs):
    event_types = defaultdict(int)
    for log in logs:
        event_types[log['event_type']] += 1
    return event_types


# Генерация статистики по пользователям
def generate_user_stats(logs):
    users = defaultdict(int)
    for log in logs:
        users[log.get('user', 'Unknown')] += 1
    return users


# Генерация статистики по источникам
def generate_source_stats(logs):
    sources = defaultdict(int)
    for log in logs:
        sources[log.get('source', 'Unknown')] += 1
    return sources


# Генерация распределения по дням недели
def generate_weekday_stats(logs):
    weekdays = Counter()
    for log in logs:
        timestamp = datetime.fromisoformat(log['timestamp'])
        weekdays[timestamp.strftime('%A')] += 1
    return weekdays


# Построение графиков
def generate_event_type_chart(stats, output_file):
    event_types = list(stats.keys())
    counts = list(stats.values())
    
    plt.figure(figsize=(10, 6))
    plt.bar(event_types, counts, color='skyblue')
    plt.xlabel("Event Type")
    plt.ylabel("Count")
    plt.title("Event Type Distribution")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()


def generate_user_activity_chart(stats, output_file):
    users = list(stats.keys())
    counts = list(stats.values())
    
    plt.figure(figsize=(10, 6))
    plt.bar(users[:10], counts[:10], color='green')  # Ограничение на 10 самых активных
    plt.xlabel("User")
    plt.ylabel("Activity Count")
    plt.title("Top 10 Users by Activity")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()


def generate_weekday_chart(stats, output_file):
    weekdays = list(stats.keys())
    counts = list(stats.values())

    plt.figure(figsize=(10, 6))
    plt.bar(weekdays, counts, color='orange')
    plt.xlabel("Day of the Week")
    plt.ylabel("Event Count")
    plt.title("Events by Day of the Week")
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()


# Генерация текстового отчёта
def generate_text_report(logs, output_dir="/home/akpchelkova/audi"):
    # Создаем директорию, если ее нет
    os.makedirs(output_dir, exist_ok=True)

    # Генерация путей файлов
    report_file = os.path.join(output_dir, "event_log_report.txt")
    event_chart_file = os.path.join(output_dir, "event_type_report.png")
    user_chart_file = os.path.join(output_dir, "user_activity_report.png")
    weekday_chart_file = os.path.join(output_dir, "weekday_distribution.png")

    # Генерация статистики
    event_type_stats = generate_event_type_stats(logs)
    user_stats = generate_user_stats(logs)
    weekday_stats = generate_weekday_stats(logs)

    # Генерация графиков
    generate_event_type_chart(event_type_stats, event_chart_file)
    generate_user_activity_chart(user_stats, user_chart_file)
    generate_weekday_chart(weekday_stats, weekday_chart_file)

    # Генерация текстового отчета
    with open(report_file, "w") as file:
        file.write("Event Log Report\n")
        file.write("=================\n\n")
        file.write(f"Total Events: {len(logs)}\n\n")

        file.write("Event Type Statistics:\n")
        for event_type, count in event_type_stats.items():
            file.write(f"  {event_type}: {count}\n")
        file.write("\n")

        file.write("User Activity:\n")
        top_users = sorted(user_stats.items(), key=lambda x: x[1], reverse=True)[:10]
        for user, count in top_users:
            file.write(f"  {user}: {count}\n")
        file.write("\n")

        file.write("Events by Day of the Week:\n")
        for day, count in weekday_stats.items():
            file.write(f"  {day}: {count}\n")
        file.write("\n")

        file.write("Source Statistics:\n")
        for source, count in generate_source_stats(logs).items():
            file.write(f"  {source}: {count}\n")

    return report_file
