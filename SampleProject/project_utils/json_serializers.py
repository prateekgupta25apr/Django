import datetime
import json

from django.core.serializers.json import DjangoJSONEncoder
from django.core.serializers.python import Serializer


class JSONSerializer(Serializer):
    """
    Class to serialize object of QuerySet and Model to JSON
    """

    def getvalue(self):
        """
        Method to return the serialized object in JSON format
        """
        # Returning the Basic Python object in JSON format
        return json.dumps(self.objects, cls=JSONFormatHelper)

    # noinspection PyProtectedMember
    def get_dump_object(self, obj):
        """
        Method for serializing the Model object
        """
        data = dict()

        # Adding the primary key of the Model with its actual name instead of "pk
        data[obj._meta.pk.attname] = self._value_from_field(obj, obj._meta.pk)

        # Adding other fields of the Model
        data.update(self._current)
        return data


class JSONFormatHelper(DjangoJSONEncoder):
    """
    Helper class for serializing datatypes which are non-serializable by default
    """

    def default(self, obj):
        """
        Method for serializing datatypes which are non-serializable by default
        """
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return ""
