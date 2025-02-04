import os
import sys
from pathlib import Path

import javaproperties

project_dir=str(Path(__file__).resolve().parent.parent).replace("\\", "/")
if project_dir[-1]!="/":
    project_dir+="/"
console_logs=True


async def load_config_value(file_path,config_properties,required_fields,
                            expected_fields):
    # noinspection PyBroadException
    try:
        missing_fields = list()

        # Check if the config file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Config file not found at: {file_path}")

        with open(file_path, 'r') as file:
            properties = javaproperties.load(file)

        for field in required_fields:
            config_properties[field] = properties.get(field, '')
            if not config_properties[field]:
                missing_fields.append(field)

        if missing_fields:
            raise ValueError(
                (f"{'These' if len(missing_fields) > 1 else 'This'} properties are missing: "
                 f"{', '.join(missing_fields)}.")
            )

        for field in expected_fields:
            config_properties[field] = properties.get(field, "")

    except Exception as e:
        print(e)
        sys.exit(0)