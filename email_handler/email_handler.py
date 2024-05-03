import os
import pprint
import re
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailHandler:
    def __init__(self, sender_email: str, sender_password: str):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.sender_email = sender_email
        self.sender_password = sender_password

    def compose_html_content(self, courses_with_signon: list, courses_without_signon: list, entry: dict):
        html_content = ""
        course_snippets = os.listdir(f"{self.script_dir}/templates/course_snippets/")

        def swap_with(key: str, value: str, string: str) -> str:
            return re.sub("__" + key.upper() + "__", str(value), string)

        def get_snippet(relative_path: str) -> str:
            with open(f"{self.script_dir}/{relative_path}", 'r') as f:
                out = f.read()
            return out

        start_snippet = get_snippet("templates/generic_snippets/start.html")
        css = get_snippet("templates/main.css")
        start_snippet = swap_with("CSS", css, start_snippet)
        html_content += start_snippet

        if len(courses_with_signon) + len(courses_without_signon) == 1:
            snippet = get_snippet("templates/generic_snippets/hello_single_course.html")
            if len(courses_with_signon) == 1:
                course = courses_with_signon[0][1]
            else:
                course = courses_without_signon[0][1]
            snippet = swap_with("NAZWAKURSU", course["name"], snippet)
            snippet = swap_with("IMIENAZWISKO", entry["username"].split(" ")[0], snippet)
            html_content += snippet
        else:
            snippet = get_snippet("templates/generic_snippets/hello_multiple_courses.html")
            snippet = swap_with("IMIENAZWISKO", entry["username"].split(" ")[0], snippet)
            html_content += snippet

        for course in courses_with_signon:
            for filename in course_snippets:
                if course[0].startswith(filename[:-5]):
                    course_snippet = get_snippet(f"templates/course_snippets/{filename}")

                    signon_snippet = get_snippet("templates/generic_snippets/signon.html")
                    signon_snippet = swap_with("IDKURSU", course[1]["id"], signon_snippet)
                    course_snippet = swap_with("SIGNON", signon_snippet, course_snippet)

                    html_content += course_snippet
                    break

        for course in courses_without_signon:
            for filename in course_snippets:
                if course[0].startswith(filename[:-5]):
                    snippet = get_snippet(f"templates/course_snippets/{filename}")
                    snippet = swap_with("SIGNON", "", snippet)
                    html_content += snippet
                    break

        html_content += get_snippet("templates/generic_snippets/end.html")

        return html_content


    def send_email(self, recipient_email, subject, html_message) -> None:
        """
        Sends a MIMEMultipart email to the recipient.
        :param recipient_email: Email address of the recipient.
        :param subject: Subject of the email.
        :param html_message: HTML message of the email.
        """
        message = MIMEMultipart()
        message['From'] = self.sender_email
        message['To'] = recipient_email
        message['Subject'] = subject
        message.attach(MIMEText(html_message, 'html'))

        session = smtplib.SMTP('smtp.gmail.com', 587)
        session.starttls()
        session.login(self.sender_email, self.sender_password)
        session.sendmail(self.sender_email, recipient_email, message.as_string())
        session.quit()
