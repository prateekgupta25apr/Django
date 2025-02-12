import asyncio
from pathlib import Path

from prateek_gupta.utils import load_config_value

project_dir = str(Path(__file__).resolve().parent.parent).replace("\\", "/")
if project_dir[-1] != "/":
    project_dir += "/"
console_logs = True

configuration_properties = dict()

try:
    from .local_settings import *

    local_run = True
except ImportError:
    local_run = False

asyncio.create_task(load_config_value(
    project_dir + "prateek_gupta/configuration.properties",
    configuration_properties,
    [],
    [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'AWS_S3_REGION_NAME',
        'AWS_STORAGE_BUCKET_NAME'
    ]
))
