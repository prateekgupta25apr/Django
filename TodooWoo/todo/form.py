from django.forms import ModelForm
from .models import Todoo
class Todooform(ModelForm):
    class Meta:
        model=Todoo
        fields=['title','memo','important']