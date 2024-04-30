#import functions_framework

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import dotenv_values

import html_generator


#@functions_framework.http  # TODO usuń komentarze
def new_response(request):
    try:
        request_json = request.get_json(silent=True)
    except:
        request_json = request

    email = request_json["form_response"]["answers"][3]["email"]
    if email is None:
        raise ValueError(f"Invalid email: {email}")
    username = request_json["form_response"]["answers"][4]["text"]
    upcoming_courses = request_json["form_response"]["answers"][0]["choices"]["labels"]
    planned_courses = request_json["form_response"]["answers"][1]["choices"]["labels"]
    wanted_courses = request_json["form_response"]["answers"][2]["choices"]["labels"]

    html = html_generator.course_summary(username, upcoming_courses, planned_courses)

    config = dotenv_values(".env")

    send_email(config["EMAILADDRSENDER"], config["EMAILPWORD"], email, "Test", html)

    return "Done."


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

# todo usuń to poniżej
import json
with open("test.json", "r") as f:
    data = json.load(f)
new_response(data)