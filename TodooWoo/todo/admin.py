from django.contrib import admin
from.models import Todoo
# Register your models here.
class TodooAdmin(admin.ModelAdmin):
    readonly_fields=('created',)
admin.site.register(Todoo,TodooAdmin)