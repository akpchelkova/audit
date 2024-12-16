import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from config import EMAIL, PASSWORD

def send_email_with_attachments(
        smtp_server="smtp.mail.ru",
        smtp_port=587,
        email_sender=EMAIL,
        email_get=EMAIL,
        email_password=PASSWORD,
        subject="Отчет по журналу событий",
        body="Вложенные файлы из указанной директории.",
        directory="/home/akpchelkova/audi"
    ):
    """
    Отправляет письмо самому себе с прикрепленными файлами из указанной директории.

    :param smtp_server: Адрес SMTP сервера
    :param smtp_port: Порт SMTP сервера
    :param email_user: Ваш адрес электронной почты
    :param email_password: Пароль от почты (или пароль приложения)
    :param subject: Тема письма
    :param body: Текст сообщения
    :param directory: Директория, из которой будут прикреплены файлы
    """
    # Создание сообщения
    msg = MIMEMultipart()
    msg['From'] = email_sender
    msg['To'] = email_get  # Отправляем самому себе
    msg['Subject'] = subject

    # Добавление тела письма
    msg.attach(MIMEText(body, 'plain'))

    # Проверка директории и добавление файлов
    if os.path.isdir(directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):  # Проверяем, что это файл
                with open(file_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f"attachment; filename={filename}")
                    msg.attach(part)
    else:
        raise FileNotFoundError(f"Указанная директория '{directory}' не существует или это не директория.")

    # Отправка письма через SMTP сервер
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Шифруем соединение
        server.login(email_sender, email_password)
        server.sendmail(email_sender, email_get, msg.as_string())
        print("Сообщение отправлено!")
    except Exception as e:
        print(f"Ошибка при отправке письма: {e}")
    finally:
        server.quit()

# Пример использования
if __name__ == "__main__":
    from config import EMAIL, PASSWORD  # Убедитесь, что у вас есть config.py с EMAIL и PASSWORD

    send_email_with_attachments(
        smtp_server="smtp.mail.ru",
        smtp_port=587,
        email_sender=EMAIL,  # Используйте email_sender вместо email_user
        email_get=EMAIL,     # Также email_get должен быть email_sender, если отправляете себе
        email_password=PASSWORD,
        subject="Отчет по журналу событий",
        body="Вложенные файлы из указанной директории.",
        directory="/home/akpchelkova/audi"
    )
