import json
import logging
import os
import pprint

import requests
from bs4 import BeautifulSoup
from dotenv import dotenv_values

from email_handler.email_handler import EmailHandler
from gsheets.gsheets import GSheets
from logger.logger import ScriptLogger
from mailerlite_handler.mailerlite import MailerLite
from teachable.teachable import Teachable


class PowiadomOStarcieKursuScript:
    def __init__(self):
        self.logger = ScriptLogger(level=logging.INFO)
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.env_config = dotenv_values(f"{self.script_dir}/.env")

        self.email_handler = EmailHandler(self.env_config["EMAILADDRSENDER"], self.env_config["EMAILPWORD"])
        self.group_ids = []
        self.mailerlite = None
        self.teachable = None
        self.gsheets = None

        # todo - change below to False on commit
        self.USE_DEV_MODE = True # if True, it will only send emails to the address below
        self.DEV_MODE_EMAIL = "pilleowo@gmail.com"

    def _init_gsheets(self):
        self.gsheets = GSheets(self.env_config["GSHEETID"], self.logger)

    def _init_mailerlite(self):
        self.mailerlite = MailerLite(self.env_config["MAILERLITEKEY"])
        with open(f"{self.script_dir}/mailerlite_handler/group_ids.json", 'r') as f:
            self.group_ids = json.load(f)

    def _init_teachable(self):
        self.teachable = Teachable(self.env_config["TEACHABLEKEY"])

    def run_for_new_entries(self) -> None:
        """
        Runs the script responsible for handling new entries in Typeform.

        1. Check if there are any new entries from Typeform.
            1.1. If there are no new entries, exit.
        2. If there are new entries, get info about courses from Teachable API
        3. For each entry:
            3.1. Check if chosen courses are published, add a suitable message to email HTML and possibly URLs?
            3.2. Add the entry email and entry time to the Mailerlite waitlists of every UNPUBLISHED
                 course that was chosen.
            3.3. Send email.
        """

        self._init_gsheets()
        new_entries = self.gsheets.check_spreadsheet_for_new_entry()
        # new_entries = []
        # with open("temp_entries.json", 'r') as f:
        #     new_entries = json.load(f)

        if len(new_entries) == 0:
            self.logger.log("No new entries detected in spreadsheet.", level=logging.DEBUG)
            return
        emails = [e['email'] for e in new_entries]
        self.logger.log(f"{len(new_entries)} new entries detected: {', '.join(emails)}")

        self._init_teachable()
        course_data = self.teachable.get_all_courses()

        self._init_mailerlite()

        for entry in new_entries:
            try:
                if self.USE_DEV_MODE and self.DEV_MODE_EMAIL != entry['email']:
                    self.logger.log("DEV MODE ACTIVE - Skipping entry.", level=logging.WARNING)
                    self.remove_entry_from_list(entry)
                    continue
                if len(entry["chosen_courses"]["upcoming"]) + len(entry["chosen_courses"]["active"]) == 0:
                    self.remove_entry_from_list(entry)
                    continue
                courses_to_include_in_email = self.parse_entry(course_data, entry)
                html_content = self.email_handler.compose_html_content(
                    courses_to_include_in_email["with_sign_on"],
                    courses_to_include_in_email["without_sign_on"],
                    entry
                )
                self.email_handler.send_email(entry["email"], "Powiadom mnie o starcie ~ NEWGRADVETS", html_content)
                self.remove_entry_from_list(entry)
                self.logger.log(f"Succesfully processed entry {entry['email']}.")
            except Exception as e:
                self.logger.log(f"Entry parsing failed: {e}", level=logging.ERROR)

    def remove_entry_from_list(self, entry):
        with open(f"{self.script_dir}/gsheets/data/entries_processing.json", "r") as f:
            entries_processing = json.load(f)
        entries_processing.remove(entry)
        with open(f"{self.script_dir}/gsheets/data/entries_processing.json", 'w') as f:
            json.dump(entries_processing, f)

    def parse_entry(self, course_data, entry):
        courses_to_include_in_email = {"with_sign_on": [], "without_sign_on": []}
        group_ids_to_add_to = []

        chosen_courses = entry["chosen_courses"]["active"] + entry["chosen_courses"]["upcoming"]
        for full_cname in chosen_courses:
            standardized_cname = full_cname.strip().split("(")[0]
            standardized_cname = self.teachable.to_lower_alphanumeric(standardized_cname)
            upcoming_course = self.teachable.get_upcoming_teachable_course(standardized_cname, course_data)
            # the following line takes a lot of time, because it is literally scraping the sales page
            # and looking for a purchase link. maybe it can somehow be optimized?
            if upcoming_course is not None and upcoming_course["is_published"] \
                    and self._check_if_course_page_contains_buy_link(upcoming_course["id"]):
                courses_to_include_in_email["with_sign_on"].append([standardized_cname, upcoming_course])
            else:
                courses_to_include_in_email["without_sign_on"].append([standardized_cname, full_cname])
                for k in self.group_ids:
                    if standardized_cname.startswith(k):
                        group_ids_to_add_to.append(self.group_ids[k])
                        break

        email = entry["email"]
        first_name = entry["username"].split(" ")[0]
        last_name = entry["username"].split(" ")[1]
        try:
            self.mailerlite.create_subscriber(email, first_name, last_name, add_to_groups=group_ids_to_add_to)
        except RuntimeError as e:
            self.logger.log(f"Adding email to Mailerlite group failed: {e}", level=logging.ERROR)
        return courses_to_include_in_email

    def _check_if_course_page_contains_buy_link(self, course_id: int) -> bool:
        url = self.teachable.get_sales_page_url(course_id)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        for button in soup.find_all('a', href=True):
            if button['href'].startswith("https://www.newgradvets.com/purchase?product_id="):
                return True
        return False


if __name__ == "__main__":
    try:
        script = PowiadomOStarcieKursuScript()
        script.run_for_new_entries()
    except Exception as e:
        self.logger.log(f"Program-wide exception occured: {e}", level=logging.CRITICAL)
