from email.mime.text import MIMEText
import smtplib
from src.config.settings import settings


async def send_email(email, subject, body, html=False):
    sender_email = settings.SMTP_EMAIL
    sender_password = settings.SMTP_PASSWORD
    recipient_email = email

    message = MIMEText(body, 'html' if html else 'plain')
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, message.as_string())

    except smtplib.SMTPAuthenticationError:
        print("Ошибка аутентификации. Проверьте свой пароль для приложений.")
    except Exception as e:
        print(f"Произошла ошибка при отправке электронной почты: {e}")
    finally:
        server.quit()
