from django.db import models


# Don't change the filename from models.py to any other as it may cause issue while
# dumping db data
class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField('First Name', max_length=100, blank=True)
    last_name = models.CharField('Last Name', max_length=100, blank=True)
    email = models.EmailField('Email', unique=True)
    password = models.BinaryField('Password')
    forgot_password_request = models.BooleanField(default=False)
    dark_mode = models.BooleanField(default=False)

    def __str__(self):
        name = self.first_name + ' ' + self.last_name
        return name

    class Meta:
        db_table = "users"
