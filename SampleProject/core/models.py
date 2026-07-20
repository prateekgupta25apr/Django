from django.db import models


class Configurations(models.Model):
    id = models.AutoField(primary_key=True)
    key = models.CharField(max_length=500)
    value = models.CharField(max_length=500)

    class Meta:
        db_table = "configurations"

    def __str__(self):
        return str(self.id)
