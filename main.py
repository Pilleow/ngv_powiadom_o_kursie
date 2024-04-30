import os
import smtplib
from datetime import datetime
from dotenv import dotenv_values
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from html_generator.html_generator import HTMLGenerator


def new_response(email):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    start = datetime.now()
    html = HTMLGenerator.generate_html(
        f"{script_dir}/html_generator/templates/time.html",
        time=str(datetime.now())
    )
    config = dotenv_values(f"{script_dir}/.env")
    send_email(
        config["EMAILADDRSENDER"],
        config["EMAILPWORD"],
        email, "Test", html
    )
    end = datetime.now()
    print(f"Sent email to {email} at {datetime.now()} - time taken: {end - start}")


def get_element(key, request):
    if request and key in request:
        return request[key]
    return None


def send_email(sender_email, sender_password, recipient_email, subject, html_message):
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject

    message.attach(MIMEText(html_message, 'html'))

    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.starttls()

    session.login(sender_email, sender_password)

    session.sendmail(sender_email, recipient_email, message.as_string())

    session.quit()


new_response("pilleowo@gmail.com")