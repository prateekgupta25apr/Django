import logging
import sys
from prateek_gupta import project_dir, console_logs
from prateek_gupta.LogManager import main_log_folder_name


log_manager_parent_package = "prateek_gupta."


class LogMessagePreProcessor(logging.Formatter):
    def format(self, record):
        log_msg = super().format(record)

        if record.name == 'uvicorn.access':
            parts = log_msg.split(" ")
            log_msg = (f"{parts[0]} {parts[1]} {parts[2]} {parts[3]} : "
                       f"""{parts[7].replace('"', '')} {parts[8]} {parts[10]}""")

        return log_msg


# For Uvicorn logs
uvicorn_logs_config = {
    'version': 1,
    'disable_existing_loggers': True,
    "filters": {
            "task_id_filter": {
                "()": log_manager_parent_package + "LogManager.FilterTaskId"
            }
        },
    'formatters': {
        'formatter': {
            '()': LogMessagePreProcessor,
            'format': ("[%(thread)d(%(threadName)s)(%(task_id)s)] "
                       "%(asctime)s.%(msecs)03d {uvicorn} : %(message)s"),
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'formatter',
            'stream': sys.stdout,
            "filters": ["task_id_filter"],
        },
        'file': {
            'level': 'DEBUG',
            'class': 'prateek_gupta.LogManager.LogFileHandler',
            'file_path': str(project_dir).replace("\\", "/") + "/" + main_log_folder_name,
            'formatter': 'formatter',
            "filters": ["task_id_filter"],
        },
    },
    'loggers': {
        'uvicorn': {
            'handlers': ['console' if console_logs else 'file'],
            'level': 'DEBUG',
            'propagate': False,
        }
    },
}
