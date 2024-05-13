import os
import pprint
import re
import json
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

        with open(f"{self.script_dir}/templates/course_snippets/snippets.json", "r") as f:
            snippet_data = json.load(f)

        def swap_with(key: str, value: str, string: str) -> str:
            return re.sub("__" + key.upper() + "__", str(value), string)

        def remove_description(string: str) -> str:
            return re.sub("<div(.|\n)*<\/div>", "", string)

        def get_snippet(relative_path: str) -> str:
            with open(f"{self.script_dir}/{relative_path}", 'r') as f:
                out = f.read()
            return out

        start_snippet = get_snippet("templates/generic_snippets/start.html")
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

        course_snippet = get_snippet("templates/course_snippets/course_snippet.html")

        for course in courses_with_signon:
            for name in snippet_data.keys():
                if course[0].startswith(name):
                    if snippet_data[name]["use_special_snippet"] != "":
                        c_sn = get_snippet(snippet_data[name]["use_special_snippet"])
                    else:
                        c_sn = course_snippet
                        c_sn = swap_with("COLOR", snippet_data[name]["color"], c_sn)
                        c_sn = swap_with("TITLE", snippet_data[name]["title"], c_sn)
                        if (snippet_data[name]["desc"] == ""):
                            c_sn = remove_description(c_sn)
                        else:
                            c_sn = swap_with("DESC", snippet_data[name]["desc"], c_sn)
                        signon_snippet = get_snippet("templates/generic_snippets/signon.html")
                        signon_snippet = swap_with("IDKURSU", course[1]["id"], signon_snippet)
                        c_sn = swap_with("SIGNON", signon_snippet, c_sn)
                    html_content += c_sn
                    break

        for course in courses_without_signon:
            for name in snippet_data.keys():
                if course[0].startswith(name):
                    if snippet_data[name]["use_special_snippet"] != "":
                        c_sn = get_snippet(snippet_data[name]["use_special_snippet"])
                    else:
                        c_sn = course_snippet
                        c_sn = swap_with("SIGNON", "", c_sn)
                        c_sn = swap_with("COLOR", snippet_data[name]["color"], c_sn)
                        c_sn = swap_with("TITLE", snippet_data[name]["title"], c_sn)
                        if (snippet_data[name]["desc"] == ""):
                            c_sn = remove_description(c_sn)
                        else:
                            c_sn = swap_with("DESC", snippet_data[name]["desc"], c_sn)
                    html_content += c_sn
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
