import json
import os
import csv
import gspread

from gspread.utils import ExportFormat
from oauth2client.service_account import ServiceAccountCredentials


class GSheets:
    def __init__(self, gsheet_id: str, scriptlogger: object):
        self.gsheet_id = gsheet_id
        self.scriptlogger = scriptlogger
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.client = self._authenticate_and_return_client()

    def _authenticate_and_return_client(self) -> gspread.Client:
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        keyfile = f'{self.script_dir}/data/.secret.json'

        creds = ServiceAccountCredentials.from_json_keyfile_name(keyfile, scope)
        return gspread.authorize(creds)

    def check_spreadsheet_for_new_entry(self) -> list[dict]:
        """
        Checks the Google Spreadsheet for new entries.
        :return: A list of new spreadsheet entries.
        """
        parse_csv = lambda data: {
            "chosen_courses": {
                "active": data[0].split(', '),
                "upcoming": data[1].split(', '),
                "not_existing": data[2].split(', '),
            },
            "email": data[3],
            "username": data[4],
            "submitted_at": data[5]
        }

        if "gsheet_new.csv" in os.listdir(f'{self.script_dir}/data/'):
            os.rename(f'{self.script_dir}/data/gsheet_new.csv', f'{self.script_dir}/data/gsheet_old.csv')
        spreadsheet = self.client.open_by_key(self.gsheet_id)
        exported = spreadsheet.export(ExportFormat.CSV)
        with open(f'{self.script_dir}/data/gsheet_new.csv', "wb+") as f:
            f.write(exported)

        if "gsheet_old.csv" not in os.listdir(f'{self.script_dir}/data/'):
            return []

        f_new = open(f'{self.script_dir}/data/gsheet_new.csv', "r")
        f_old = open(f'{self.script_dir}/data/gsheet_old.csv', "r")

        old_data = csv.reader(f_old, delimiter=',')
        new_data = csv.reader(f_new, delimiter=',')
        output = []
        while True:
            new_item = next(new_data, None)
            old_item = next(old_data, None)
            if new_item is None:
                break
            if old_item is None:
                output.append(parse_csv(new_item))

        f_new.close()
        f_old.close()

        # local new entries backup in case program stops execution before completing processing
        with open(f"{self.script_dir}/data/entries_processing.json", "r") as f:
            entries_processing = json.load(f)
        for entry in output:
            if entry not in entries_processing:
                entries_processing.append(entry)
        with open(f"{self.script_dir}/data/entries_processing.json", 'w') as f:
            json.dump(entries_processing, f)

        return entries_processing
