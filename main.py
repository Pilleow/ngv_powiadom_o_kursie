import logging
import os
import pprint
import smtplib
from datetime import datetime
from dotenv import dotenv_values
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from html_generator.html_generator import HTMLGenerator
from logger.logger import ScriptLogger
from gsheets.gsheets import GSheets


class PowiadomOStarcieKursuScript:
    def __init__(self):
        self.logger = ScriptLogger(level=logging.INFO)
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.env_config = dotenv_values(f"{self.script_dir}/.env")
        self.gsheets = GSheets(self.env_config["GSHEETID"], self.logger)

    def run_for_waitlist(self) -> None:
        """
        Runs the script responsible for handling the waitlist and possible update notifications.

        1. Get info about courses from Teachable API
        2. For every list in waitlists.json:
            2.1. If a course changed state from Unpublished to Published, send update emails to all emails in waitlist,
                 be wary of the quota: https://support.google.com/a/answer/166852?hl=en
                 maybe send them in 90 Bcc recipient batches? todo: figure it out
            2.2. Once all emails get sent, add all emails and entry times to a separate list such as "previous".
        """
        pass

    def run_for_new_entries(self) -> None:
        """
        Runs the script responsible for handling new entries in Typeform.

        1. Check if there are any new entries from Typeform.
            1.1. If there are no new entries, exit.
        2. If there are new entries, get info about courses from Teachable API
        3. For each entry:
            3.1. Check if chosen courses are published, add a suitable message to email HTML and possibly URLs?
            3.2. Add the entry email and entry time to the lists of every UNPUBLISHED course that was chosen.
            3.3. Send email.
        """
        new_entries = self.gsheets.check_spreadsheet_for_new_entry()
        if len(new_entries) == 0:
            self.logger.log("No new entries detected in spreadsheet.", level=logging.DEBUG)
            return

        self.logger.log(f"{len(new_entries)} new entries detected. Proceeding to email generation.")
        for entry in new_entries:
            pass
            # todo - add point 3.

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
    script.run_for_new_entries()
