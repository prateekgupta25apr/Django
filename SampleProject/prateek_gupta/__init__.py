import asyncio
from pathlib import Path

from prateek_gupta.utils import (load_properties_from_file)
from .project_settings import *

project_dir = str(Path(__file__).resolve().parent.parent).replace("\\", "/")
if project_dir[-1] != "/":
    project_dir += "/"

module_lock_message="Module is disabled,please contact admin"

configuration_properties = dict()

pre_construct_method_dict = {}


def pre_construct_method(*args, **kwargs):
    def pre_construct_method_args(function_name):
        pre_construct_method_dict[function_name.__name__] = {
            "function": function_name, "args": args, "kwargs": kwargs}
        return function_name

    return pre_construct_method_args


post_construct_method_dict = {}


def post_construct_method(*args, **kwargs):
    def post_construct_method_args(function_name):
        post_construct_method_dict[function_name.__name__] = {
            "function": function_name, "args": args, "kwargs": kwargs}
        return function_name

    return post_construct_method_args


@pre_construct_method()
async def load_config_properties_fom_file():
    global configuration_properties
    configuration_properties = await load_properties_from_file(
        configuration_properties_file_path,
        required_fields,
        expected_fields, False
    )


@pre_construct_method()
async def load_exception_messages():
    configuration_properties["exception_messages"] = await load_properties_from_file(
        project_dir + "ServiceExceptionMessages.properties",
        [],
        [],
        True
    )


async def import_modules():
    if not scanned_files:
        import os
        for root, dirs, files in os.walk(project_dir):
            for file in files:
                if file.endswith(".py") and "views" in file and not file.startswith("__"):
                    module_name = ((root + "/" + file)
                                   .replace(project_dir, "")
                                   .replace("/", ".")
                                   .replace(".py", ""))
                    scanned_files.append(module_name)

    for module_name in scanned_files:
        # noinspection PyBroadException
        try:
            import importlib
            importlib.import_module(module_name)
        except Exception:
            from exceptions import log_error
            log_error()


async def pre_construct_method_execution():
    await import_modules()
    print("PreConstructMethods : ", pre_construct_method_dict)

    for function_name, details in pre_construct_method_dict.items():
        if asyncio.iscoroutinefunction(details.get("function")):
            await details.get("function")(*details.get("args", []),
                                          **details.get("kwargs", {}))
        else:
            details.get("function")(*details.get("args", []), **details.get("kwargs", {}))


async def post_construct_method_execution():
    print("PostConstructMethods : ", post_construct_method_dict)

    for function_name, details in post_construct_method_dict.items():
        if asyncio.iscoroutinefunction(details.get("function")):
            await details.get("function")(*details.get("args", []),
                                          **details.get("kwargs", {}))
        else:
            details.get("function")(*details.get("args", []), **details.get("kwargs", {}))
