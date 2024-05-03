import os
import json
import pprint
import re
import smtplib
import logging
import requests
from dotenv import dotenv_values
from datetime import date, datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from bs4 import BeautifulSoup
from gsheets.gsheets import GSheets
from logger.logger import ScriptLogger
from teachable.teachable import Teachable
from html_generator.html_generator import HTMLGenerator


class PowiadomOStarcieKursuScript:
    def __init__(self):
        self.months = {
            "styczeń": 1,
            "luty": 2,
            "marzec": 3,
            "kwiecień": 4,
            "maj": 5,
            "czerwiec": 6,
            "lipiec": 7,
            "sierpień": 8,
            "wrzesień": 9,
            "październik": 10,
            "listopad": 11,
            "grudzień": 12
        }

        self.logger = ScriptLogger(level=logging.INFO)
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.env_config = dotenv_values(f"{self.script_dir}/.env")

        self.teachable = Teachable(self.env_config["TEACHABLEKEY"])
        self.gsheets = GSheets(self.env_config["GSHEETID"], self.logger)

    def run_for_new_entries(self) -> None:
        """
        Runs the script responsible for handling new entries in Typeform.

        1. Check if there are any new entries from Typeform.
            1.1. If there are no new entries, exit.
        2. If there are new entries, get info about courses from Teachable API
        3. For each entry:
            3.1. Check if chosen courses are published, add a suitable message to email HTML and possibly URLs?
            3.2. Add the entry email and entry time to the Mailerlite waitlists of every UNPUBLISHED course that was chosen.
            3.3. Send email.
        """

        # todo - uncomment and delete json entries
        # new_entries = self.gsheets.check_spreadsheet_for_new_entry()
        new_entries = []
        with open("temp_entries.json", 'r') as f:
            new_entries = json.load(f)

        if len(new_entries) == 0:
            self.logger.log("No new entries detected in spreadsheet.", level=logging.DEBUG)
            return
        self.logger.log(f"{len(new_entries)} new entries detected.")

        course_data = self.teachable.get_all_courses()
        # with open("temp.json", "w") as f:
        #     json.dump(course_data, f, indent=2)

        for entry in new_entries:
            courses_to_include_in_email = {
                "with_sign_on": [],
                "without_sign_on": []
            }
            for cname in entry["chosen_courses"]["active"]:
                cname_start = cname.strip().split("(")[0]
                cname_start = re.sub(r'[^a-zA-Z0-9]', '', cname_start).lower()
                matching_courses = []

                # 1. find all courses matching the name
                for course in course_data["courses"]:
                    c_name_clean = re.sub(r'[^a-zA-Z0-9]', '', course["name"]).lower()
                    if c_name_clean.startswith(cname_start):
                        matching_courses.append(course)

                # 2. select the first upcoming course
                upcoming_course = None
                upcoming_course_date = date(year=2099, month=1, day=7)
                today_date = date.today()
                for m_course in matching_courses:
                    name_split = m_course["name"].strip().split(" ")
                    try:
                        month = self.months[name_split[-2].lower()]
                        year = int(name_split[-1])
                    except (KeyError, ValueError):
                        continue
                    course_date = date(year=year, month=month, day=7)
                    delta_current = upcoming_course_date - today_date
                    delta_course = course_date - today_date
                    if delta_course.days < 0:
                        continue
                    if delta_current.days > delta_course.days:
                        upcoming_course = m_course
                        upcoming_course_date = course_date

                # 3. do stuff with upcoming course
                print(f"\n\n dla: {cname}")
                pprint.pprint(upcoming_course)
                print(upcoming_course_date.strftime("%B %d, %Y"))

    def _check_if_course_page_contains_buy_link(self, course_id: int) -> bool:
        url = self.teachable.get_sales_page_url(course_id)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        # with open("temp.html", 'w') as f:
        #     f.write(soup.prettify())
        for button in soup.find_all('a', href=True):
            if button['href'].startswith("https://www.newgradvets.com/purchase?product_id="):
                return True
        return False

    def _send_email(self, recipient_email, subject, html_message) -> None:
        """
        Sends a MIMEMultipart email to the recipient.
        :param recipient_email: Email address of the recipient.
        :param subject: Subject of the email.
        :param html_message: HTML message of the email.
        """
        message = MIMEMultipart()
        message['From'] = config["EMAILADDRSENDER"]
        message['To'] = recipient_email
        message['Subject'] = subject
        message.attach(MIMEText(html_message, 'html'))

        session = smtplib.SMTP('smtp.gmail.com', 587)
        session.starttls()
        session.login(config["EMAILADDRSENDER"], config["EMAILPWORD"])
        session.sendmail(config["EMAILADDRSENDER"], recipient_email, message.as_string())
        session.quit()

    # def run_for_waitlist(self) -> None:
    #     """
    #     Runs the script responsible for handling the waitlist and possible update notifications.
    #
    #     1. Get info about courses from Teachable API
    #     2. If a course changed state from Unpublished to Published:
    #         2.1  download recipient list of the course from Mailerlite API.
    #         2.2. send update emails to all emails in waitlist, maybe send them in 90 Bcc recipient batches?
    #              also, what if someone presses the "Published" button on accident?
    #         2.3. Once all emails get sent, add all emails and entry times to a separate list such as "previous".
    #     """
    #     pass


if __name__ == "__main__":
    script = PowiadomOStarcieKursuScript()
    script.run_for_new_entries()