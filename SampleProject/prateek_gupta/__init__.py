import asyncio
import threading
from pathlib import Path

import javaproperties

from prateek_gupta.utils import load_config_value_from_file
from .project_settings import *

project_dir = str(Path(__file__).resolve().parent.parent).replace("\\", "/")
if project_dir[-1] != "/":
    project_dir += "/"

configuration_properties = dict()


async def on_load():
    load_config_task = asyncio.create_task(load_config_value_from_file(
        configuration_properties_file_path,
        configuration_properties,
        required_fields,
        expected_fields
    ))

    await load_config_task

    # Loading exceptions
    with open(project_dir+"ServiceExceptionMessages.properties", 'r') as file:
        exception_messages = javaproperties.load(file)
        configuration_properties["exception_messages"]=exception_messages

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
