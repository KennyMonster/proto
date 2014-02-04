"""
Classes to define a custom self-validating protocol
"""
import json


class ValidationError(Exception):
    pass


class Field(object):
    """
    An individual field of a protocol message
    """
    def __init__(self, required=True, default=None):
        self.default = default
        self.required = required

    def validate(self, value):
        if value is None and self.required:
            raise ValidationError("Values is required but is not set")

    def default_value(self):
        return self.default

    def _not_required_and_none(self, value):
        if not self.required and value is None:
            return True


class NumberField(Field):
    def validate(self, value):
        if self._not_required_and_none(value):
            return

        # http://stackoverflow.com/questions/8169001/why-is-bool-a-subclass-of-int
        if isinstance(value, bool):
            raise ValidationError("Boolean is not a valid number")
        if not isinstance(value, (int, long, float, complex)):
            raise ValidationError("%s is not a valid number" % value)

        super(NumberField, self).validate(value)


class BooleanField(Field):
    def validate(self, value):
        if self._not_required_and_none(value):
            return

        if not isinstance(value, bool):
            raise ValidationError("%s is not a boolean" % value)

        super(BooleanField, self).validate(value)


class CharField(Field):
    def validate(self, value):
        if self._not_required_and_none(value):
            return

        if not isinstance(value, basestring):
            raise ValidationError("%s is not a string - implicit casing is not performed" % value)

        super(CharField, self).validate(value)


class ProtocolMetaclass(type):
    """
    Special handling of all protocol field class variables

    Proto fields are removed from the class object and stored in
    a dict named Class._proto_fields. This avoids accidental access
    from an instance boject
    """
    def __new__(cls, clsname, bases, dct):
        class_attrs = {}
        proto_fields = {}
        for name, val in dct.items():
            if isinstance(val, Field):
                proto_fields[name] = val
            else:
                class_attrs[name] = val

        class_attrs['_proto_fields'] = proto_fields

        return super(ProtocolMetaclass, cls).__new__(cls, clsname, bases, class_attrs)


class Protocol(object):
    """
    Base class of a protocol message
    """
    __metaclass__ = ProtocolMetaclass

    def __init__(self, **kwargs):
        proto_fields = self.__class__._proto_fields

        # Create default instances of field values on the instance
        for name, field_obj in proto_fields.items():
            self.__setattr__(name, field_obj.default_value())

        # Assign ctor args to obj attrs
        for name, val in kwargs.items():
            if name in proto_fields.keys():
                self.__setattr__(name, val)
            else:
                raise NameError("%s is not defined" % name)

        super(Protocol, self).__init__()

    def serialize(self):
        """
        Returns a JSON string
        """
        self.validate()

        d = {}

        proto_fields = self.__class__._proto_fields
        for name, field_obj in proto_fields.items():
            local_attr = self.__getattribute__(name)
            if local_attr is not None:
                d[name] = local_attr

        return json.dumps(d)

    @classmethod
    def deserialize(cls, json_str):
        """
        Return a protocol object from a JSON string
        """
        obj = cls()

        json_obj = json.loads(json_str)
        for name, val in json_obj.items():
            obj.__setattr__(name, val)

        obj.validate()
        return obj

    def validate(self):
        """
        Validates the type and requirement of all protocol fields
        """
        proto_fields = self.__class__._proto_fields
        for name, field_obj in proto_fields.items():
            local_attr = self.__getattribute__(name)
            field_obj.validate(local_attr)
