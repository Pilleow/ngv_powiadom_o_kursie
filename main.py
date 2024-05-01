import os
import pprint
import smtplib
from datetime import datetime
from dotenv import dotenv_values
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from html_generator.html_generator import HTMLGenerator
from gsheets.gsheets import GSheets


class PowiadomOStarcieKursuScript:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.env_config = dotenv_values(f"{self.script_dir}/.env")
        self.gsheets = GSheets(self.env_config["GSHEETID"])

    def run(self) -> None:
        """
        Runs the script.
        """
        new_entries = self.gsheets.check_spreadsheet_for_new_entry()
        pprint.pprint(new_entries)

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

if __name__ == "__main__":
    script = PowiadomOStarcieKursuScript()
    script.run()