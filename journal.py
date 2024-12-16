import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
from report_generator import ( 
    load_logs,
    #generate_event_type_stats,
    generate_text_report,
    #save_chart_to_file
)

from send_report import send_email_with_attachments

# Функция для обновления таблицы с результатами фильтрации
def update_table(tree, logs, columns):
    for row in tree.get_children():
        tree.delete(row)

    # Добавляем строку с порядковым номером
    for index, log in enumerate(logs, start=1):
        # Вставляем данные для каждой строки таблицы
        if 'local_address' in log and 'remote_address' in log and 'status' in log:
            # Форматируем local_address и remote_address как "IP:порт"
            local_address = f"{log['local_address']['ip']}:{log['local_address']['port']}" if isinstance(log['local_address'], dict) else log['local_address']
            remote_address = f"{log['remote_address']['ip']}:{log['remote_address']['port']}" if isinstance(log['remote_address'], dict) else log['remote_address']
            row_data = [
                index, 
                log['timestamp'], 
                log['source'], 
                log['event_type'], 
                local_address,  # Теперь отображается как IP:порт
                remote_address,  # Теперь отображается как IP:порт
                log['status']
            ]
        elif 'src_path' in log:  # Для изменений файлов
            row_data = [
                index, 
                log['timestamp'], 
                log['source'], 
                log['event_type'], 
                log['src_path'], 
            ]
        else:  # Для процессов
            row_data = [
                index, 
                log['timestamp'], 
                log['source'], 
                log['event_type'], 
                log.get('pid'), 
                log.get('user', '')
            ]
        tree.insert("", "end", values=row_data[:len(columns)])

# Функция для обработки сортировки по столбцам
def sort_column(treeview, col, reverse):
    data = [(treeview.item(item)['values'], item) for item in treeview.get_children('')]
    data.sort(key=lambda x: x[0][col], reverse=reverse)
    
    for i, (values, item) in enumerate(data):
        treeview.item(item, values=values)
    
    return not reverse

# Функция для отправки письма
def send_report_email():
    try:
        # Вызов функции для отправки письма с вложениями
        send_email_with_attachments()
        # Уведомление об успешной отправке
        messagebox.showinfo("Success", "Email sent successfully.")
    except Exception as e:
        # Уведомление об ошибке, если что-то пошло не так
        messagebox.showerror("Error", f"Error sending email: {e}")


# Функция для фильтрации логов (заменена на простую фильтрацию)
def filter_logs(logs, event_type, user, source, start_time=None, end_time=None):
    filtered_logs = []
    for log in logs:
        if event_type and event_type not in log.get('event_type', ''):
            continue
        if user and user not in log.get('user', ''):
            continue
        if source and source not in log.get('source', ''):
            continue
        if start_time and log.get('timestamp') < start_time:
            continue
        if end_time and log.get('timestamp') > end_time:
            continue
        filtered_logs.append(log)
    return filtered_logs

# Обработчик поиска
def search_logs():
    event_type = event_type_var.get()
    user = user_var.get()
    source = source_var.get()
    start_time_str = start_time_var.get()
    end_time_str = end_time_var.get()

    # Преобразование строк времени в объекты datetime
    start_time = None
    end_time = None
    if start_time_str:
        try:
            start_time = datetime.fromisoformat(start_time_str)
        except ValueError:
            pass

    if end_time_str:
        try:
            end_time = datetime.fromisoformat(end_time_str)
        except ValueError:
            pass

    # Загружаем логи
    logs = load_logs()

    # Фильтруем логи по source для каждой вкладки
    selected_tab = notebook.index(notebook.select())  # Получаем индекс текущей вкладки

    if selected_tab == 0:  # Вкладка "Network Monitoring"
        filtered_logs = filter_logs(logs, event_type, user, source='network', start_time=start_time, end_time=end_time)
        update_table(network_tree, filtered_logs, network_columns)
    elif selected_tab == 1:  # Вкладка "Process Monitoring"
        filtered_logs = filter_logs(logs, event_type, user, source='process', start_time=start_time, end_time=end_time)
        update_table(process_tree, filtered_logs, process_columns)
    elif selected_tab == 2:  # Вкладка "File Change Monitoring"
        filtered_logs = filter_logs(logs, event_type, user, source='file', start_time=start_time, end_time=end_time)
        update_table(file_tree, filtered_logs, file_columns)

# Функция для генерации отчета
def generate_report():
    
    

    #report_file = generate_text_report(logs)
    try:
        # Загружаем логи
        #log_file = "event_log.json"
        logs = load_logs()
        if not logs:
            messagebox.showerror("Error", "No logs found.")
            return

        # Генерируем статистику по типам событий
        #event_type_stats = generate_event_type_stats(logs)

        # Сохраняем отчет в текстовом формате
        report_file = generate_text_report(logs)
        messagebox.showinfo("Report", f"Report generated successfully: {report_file}")

        # Сохраняем график
        #save_chart_to_file(event_type_stats)
        #messagebox.showinfo("Chart", "Chart saved as event_type_report.png")

    except Exception as e:
        messagebox.showerror("Error", f"Error generating report: {e}")

# Создание основного окна Tkinter
root = tk.Tk()
root.title("Event Log Viewer")

# Создание вкладок с использованием ttk.Notebook
notebook = ttk.Notebook(root)
notebook.pack(padx=10, pady=10, fill="both", expand=True)

# Вкладка мониторинга сети
network_tab = ttk.Frame(notebook)
notebook.add(network_tab, text="Network Monitoring")

# Вкладка мониторинга процессов
process_tab = ttk.Frame(notebook)
notebook.add(process_tab, text="Process Monitoring")

# Вкладка мониторинга изменений файлов
file_tab = ttk.Frame(notebook)
notebook.add(file_tab, text="File Change Monitoring")

# Создание виджетов для ввода критериев поиска
frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

tk.Label(frame, text="Event Type:").grid(row=0, column=0, sticky="w")
event_type_var = tk.StringVar()
event_type_entry = tk.Entry(frame, textvariable=event_type_var)
event_type_entry.grid(row=0, column=1)

tk.Label(frame, text="User:").grid(row=1, column=0, sticky="w")
user_var = tk.StringVar()
user_entry = tk.Entry(frame, textvariable=user_var)
user_entry.grid(row=1, column=1)

tk.Label(frame, text="Source:").grid(row=2, column=0, sticky="w")
source_var = tk.StringVar()
source_entry = tk.Entry(frame, textvariable=source_var)
source_entry.grid(row=2, column=1)

tk.Label(frame, text="Start Time (YYYY-MM-DDTHH:MM:SS):").grid(row=3, column=0, sticky="w")
start_time_var = tk.StringVar()
start_time_entry = tk.Entry(frame, textvariable=start_time_var)
start_time_entry.grid(row=3, column=1)

tk.Label(frame, text="End Time (YYYY-MM-DDTHH:MM:SS):").grid(row=4, column=0, sticky="w")
end_time_var = tk.StringVar()
end_time_entry = tk.Entry(frame, textvariable=end_time_var)
end_time_entry.grid(row=4, column=1)

search_button = tk.Button(frame, text="Search", command=search_logs)
search_button.grid(row=5, column=0, columnspan=2, pady=10)

# Создание кнопки для генерации отчета
report_button = tk.Button(frame, text="Generate Report", command=generate_report)
report_button.grid(row=6, column=0, columnspan=2, pady=10)

# Создание кнопки для отправления письма
send_email_button = tk.Button(frame, text="Send Email with Attachments", command=send_report_email)
send_email_button.grid(row=7, column=0, columnspan=2, pady=10)

# Создание таблиц для отображения результатов для каждой вкладки
network_columns = ("#", "Timestamp", "Source", "Event Type", "Local Address", "Remote Address", "Status")
process_columns = ("#", "Timestamp", "Source", "Event Type", "Process ID", "User")
file_columns = ("#", "Timestamp", "Source", "Event Type", "File Path")

network_tree = ttk.Treeview(network_tab, columns=network_columns, show="headings", height=10)
network_tree.pack(padx=10, pady=10, fill="both", expand=True)

process_tree = ttk.Treeview(process_tab, columns=process_columns, show="headings", height=10)
process_tree.pack(padx=10, pady=10, fill="both", expand=True)

file_tree = ttk.Treeview(file_tab, columns=file_columns, show="headings", height=10)
file_tree.pack(padx=10, pady=10, fill="both", expand=True)


# Добавление прокрутки с обычным ползунком
scrollbar = ttk.Scrollbar(root, orient="vertical")
scrollbar.pack(side="right", fill="y")

# Привязка прокрутки ко всем таблицам
network_tree.configure(yscrollcommand=scrollbar.set)
process_tree.configure(yscrollcommand=scrollbar.set)
file_tree.configure(yscrollcommand=scrollbar.set)
scrollbar.config(command=lambda *args: [network_tree.yview(*args), process_tree.yview(*args), file_tree.yview(*args)])

# Сортировка по колонке при клике на заголовок
reverse_sort = {col: False for col in network_columns + process_columns + file_columns}

def on_column_click(tree, col, reverse):
    data = [(tree.item(item)['values'], item) for item in tree.get_children('')]
    data.sort(key=lambda x: x[0][col], reverse=reverse)
    
    for i, (values, item) in enumerate(data):
        tree.item(item, values=values)
    
    return not reverse

# Привязка обработчиков кликов по колонкам для каждой таблицы
for idx, col in enumerate(network_columns):
    network_tree.heading(col, text=col, command=lambda idx=idx: on_column_click(network_tree, idx, reverse_sort[network_columns[idx]]))

for idx, col in enumerate(process_columns):
    process_tree.heading(col, text=col, command=lambda idx=idx: on_column_click(process_tree, idx, reverse_sort[process_columns[idx]]))

for idx, col in enumerate(file_columns):
    file_tree.heading(col, text=col, command=lambda idx=idx: on_column_click(file_tree, idx, reverse_sort[file_columns[idx]]))

# Запуск главного цикла Tkinter
root.mainloop()
