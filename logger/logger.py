import logging
import datetime
import os


class ScriptLogger:
    def __init__(self, level:int=logging.INFO):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        strf_format = ("%Y_%m_%d")
        today = datetime.date.today()
        log_exists = False
        if f'log_{today.strftime(strf_format)}.log' in os.listdir(f'{self.script_dir}/'):
            log_exists = True
        logging.basicConfig(level=level,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            filename=f'{self.script_dir}/log_{today.strftime(strf_format)}.log',
                            filemode='a')
        self.logger = logging.getLogger()

        if not log_exists:
            self.logger.info(f"Logging started at level {self.logger.level} in file log_{today.strftime(strf_format)}.log")
            self.logger.info(f"\"NGV Powiadom o starcie kursu\" script started on {datetime.datetime.now()}\n")

        month_ago = today - datetime.timedelta(days=30)
        if f'log_{month_ago.strftime(strf_format)}.log' in os.listdir(f'{self.script_dir}/'):
            os.remove(f'log_{month_ago.strftime(strf_format)}.log')
            self.log("Log from 30 days ago has been automatically removed.")

    def log(self, msg: str, level: int = logging.INFO, exc_info: int = None):
        self.logger.log(level=level, msg=msg, exc_info=exc_info)
