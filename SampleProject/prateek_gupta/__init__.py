import asyncio
import threading
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


async def on_load():
    load_config_task = asyncio.create_task(load_config_value(
        project_dir + "prateek_gupta/configuration.properties",
        configuration_properties,
        [],
        [
            'AWS_ACCESS_KEY_ID',
            'AWS_SECRET_ACCESS_KEY',
            'AWS_S3_REGION_NAME',
            'AWS_STORAGE_BUCKET_NAME',
            'KAFKA_ENABLE',
            'KAFKA_BROKER',
            'KAFKA_CONSUMER_GROUP',
            'KAFKA_SECURITY_PROTOCOL',
            'KAFKA_SASL_MECHANISM',
            'KAFKA_SASL_USERNAME',
            'KAFKA_SASL_PASSWORD',
            'KAFKA_AWS_CA_FILE_PATH'
        ]
    ))

    await load_config_task

    enable_kafka = configuration_properties.get("KAFKA_ENABLE", None)
    if enable_kafka and enable_kafka == "S":
        # Setting up sync kafka in a separate thread
        from .kafka_sync import setup_sync_kafka
        consumer_thread = threading.Thread(target=setup_sync_kafka, daemon=True,
                                           args=(["test"],))
        consumer_thread.start()
    elif enable_kafka and enable_kafka == "A":
        configuration_properties["KAFKA_AWS_CA_FILE_PATH"] = project_dir + "AmazonRootCA1.pem"
        from .kafka_async import setup_async_kafka
        asyncio.create_task(setup_async_kafka(["test"]))
