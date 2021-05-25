import copy
import inspect
from typing import Dict

from . import fields
from .exceptions import ReadOnlyException

IGNORE_HIDDEN_ATTRIBUTE = True


class ModelMeta(type):
    def __new__(cls, name, bases, attrs):
        fields = {}
        for k, v in attrs.items():
            if isinstance(v, property) and not k.startswith('_'):
                fields[k] = v
        for base in bases:
            if hasattr(base, "_property_fields"):
                fields.update(base._property_fields)
        attrs["_property_fields"] = fields

        return type.__new__(cls, name, bases, attrs)


class ModelMixin(metaclass=ModelMeta):
    _attributes_cached = {}

    def __init__(self, *args, **kwargs):
        attrs = self._get_attributes()
        for k, v in kwargs.items():
            if k not in attrs and not isinstance(kwargs[k], fields.DataField) and k not in self._property_fields:
                raise Exception(f'{k} not in attrs')
            setattr(self, k, v)

    @classmethod
    def _get_attributes(cls) -> Dict[str, fields.DataField]:
        if cls._attributes_cached:
            return cls._attributes_cached
        attributes = inspect.getmembers(cls, lambda a: not (inspect.isroutine(a)))
        obj_attrs = [a for a in attributes if not (a[0].startswith('__') and a[0].endswith('__'))]

        retl = {}
        for obj in obj_attrs:
            (_attr_name, attr) = obj
            if isinstance(attr, fields.DataField):
                retl[_attr_name] = attr
        cls._attributes_cached = retl
        return retl

    def __setattr__(self, attr_name: str, value):
        from .models import Nested
        attributes_dict = self._get_attributes()
        if attr_name in attributes_dict:
            attr = attributes_dict[attr_name]
            current_val = getattr(self, attr_name)
            if attr.readonly and current_val is not None:
                # We allow to set the attribute if it was not set before
                if current_val != value:
                    raise ReadOnlyException(f'{attr_name} attribute is read_only !')
            if value is not None:
                if isinstance(attr, fields.ListField):
                    ret_value = []
                    for _ in value:
                        if isinstance(_, Nested):
                            ret_value.append(_)
                        else:
                            ret_value.append(attr.nested(**_))
                    value = ret_value
                elif isinstance(attr, fields.DictNestedField):
                    if not isinstance(value, Nested):
                        value = attr.nested_type(**value)
        return super().__setattr__(attr_name, value)

    def __repr__(self):
        data = self.to_dict()
        repr_str = [f'{k}={v}' for k, v in data.items()]
        return f'<{self.__class__.__name__} {" ".join(repr_str)}>'

    def __getattribute__(self, item: str):
        attr = object.__getattribute__(self, item)

        if isinstance(attr, fields.DataField):
            return copy.deepcopy(attr.default)
        else:
            return attr

    def to_dict(self):
        data = {}
        for attr_name, _ in self._get_attributes().items():
            v = getattr(self, attr_name)
            if v is None:
                continue
            data[attr_name] = v
        for attr_name, _attr_method in self._property_fields.items():
            data[attr_name] = getattr(self, attr_name)

        return {k: v for k, v in data.items() if not (k.startswith('_') and IGNORE_HIDDEN_ATTRIBUTE)}
