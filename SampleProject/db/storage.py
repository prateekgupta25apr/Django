import asyncio
import os
from concurrent.futures import Future

from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible

from prateek_gupta.aws_async import check_file_existence, upload
from prateek_gupta.thread_manager import executor


@deconstructible
class MyStorage(Storage):
    def get_valid_name(self, name):
        return name

    def _save(self, name, content):
        """
        Saves new content to the storage system.
        Calls the subclass's _save() implementation.
        """
        if not self.exists(name):
            future: Future = executor.submit(
                asyncio.run,
                upload(file=content.file, file_key=name, content_type=content.content_type))
            future.result()
        return name

    def exists(self, name):
        future: Future = executor.submit(asyncio.run, check_file_existence(name))
        result = future.result()
        return result

    def url(self, name):
        return f"/get_attachment?file_name={name}"


class FilePathBuilder:
    """Class to build the file path"""

    def __init__(self, model_name, field_name=None):
        self.model_name = model_name
        self.field_name = field_name

    def __call__(self, instance, filename):
        file_name, ext = os.path.splitext(filename)

        if self.model_name == "Table1AttachmentMapping":
            return f"Table1AttachmentMapping/{instance.table_1}/{file_name}{ext}"

        return filename

    def deconstruct(self):
        return (
            f"{self.__class__.__module__}.{self.__class__.__name__}",
            [self.model_name],
            {"field_name": self.field_name},
        )
