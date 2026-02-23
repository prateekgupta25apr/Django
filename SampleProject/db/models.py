from django.db import models

from db.storage import FilePathBuilder, MyStorage


class Table1(models.Model):
    primary_key = models.IntegerField(primary_key=True)
    col_1 = models.CharField(max_length=500, null=True, blank=True)
    col_2 = models.BooleanField(null=True, blank=True)

    class Meta:
        db_table = "table_1"

    def __str__(self):
        return str(self.primary_key)


class Table1AttachmentMapping(models.Model):
    primary_key = models.IntegerField(primary_key=True)
    table_1 = models.ForeignKey(
        Table1, on_delete=models.CASCADE, db_column='table_1_primary_key')
    attachment_path = models.ImageField(
        blank=True,
        upload_to=FilePathBuilder(
            "Table1AttachmentMapping", "attachment_path"),
        storage=MyStorage
    )

    class Meta:
        db_table = "table_1_attachment_mapping"
