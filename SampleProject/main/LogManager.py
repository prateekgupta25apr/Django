import logging
import os
import re
import shutil
from datetime import datetime

from SampleProject.settings import BASE_DIR

file_path = str(BASE_DIR).replace("\\", "/") + "/logs/"
main_log_file = file_path + "logs.log"
max_file_size = 1024 * 1024 * 10  # 10MB


def get_log_files_details():
    log_files = dict()
    # Regular expression pattern to match the desired file names
    pattern = re.compile(r'^logs\.(\d{4}-\d{2}-\d{2})\.\d+\.log$')

    # Get list of all files in the directory
    all_files = os.listdir(file_path)

    # Filter files that match the specified pattern
    target_files = [file for file in all_files if pattern.match(file)]

    for file in target_files:
        key = pattern.match(file).group(1)
        filenames = log_files.get(key, list())
        filenames.append(file)
        log_files[key] = filenames

    return log_files


class LogFileLogger:
    def __init__(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        handler = LogFileHandler(file_path + "logs.log")
        handler.setFormatter(logging.Formatter(
            fmt="%(asctime)s.%(msecs)03d %(funcName)s(){%(filename)s} : %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"))
        self.logger.addHandler(handler)
        super().__init__()


class LogFileHandler(logging.FileHandler):
    def __init__(self, filename, filemode="a"):
        self.last_log_file_date = "1999-04-25"
        self.log_file_next_serial_number = 1

        # Getting log files details as dict
        log_files = get_log_files_details()

        # Initializing last_log_file_date and log_file_next_serial_number
        if len(log_files.keys()) > 0:
            # As the self.log_files will be ordered according to dates in ascending order
            # so getting last date
            self.last_log_file_date = list(log_files.keys())[-1]

            # Plus one to track next log file serial number
            self.log_file_next_serial_number = (
                    len(log_files[self.last_log_file_date]) + 1)
        super().__init__(filename, mode=filemode)

    def handle(self, record):
        if os.path.getsize(main_log_file) > max_file_size:
            # noinspection PyBroadException
            try:
                self.close()

                shutil.copy(main_log_file, file_path + self.get_log_file_name())

                self.last_log_file_date = datetime.now().strftime("%Y-%m-%d")
                self.log_file_next_serial_number += 1

                self.stream = open(main_log_file, "w")
            except Exception:
                print("Error occurred while printing logs")
        return super().handle(record)

    def get_log_file_name(self):
        log_file_date = datetime.strptime(self.last_log_file_date, "%Y-%m-%d").date()
        if (datetime.now().date() - log_file_date).days >= 1:
            self.log_file_next_serial_number = 1

        return ("logs." + datetime.now().strftime("%Y-%m-%d") + "." +
                str(self.log_file_next_serial_number) + ".log")


# For logging
logger = LogFileLogger().logger
