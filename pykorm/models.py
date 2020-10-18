from typing import Dict

import dpath.util

from . import fields
from . import query as pykorm_query
from .meta import ModelMixin

IGNORE_HIDDEN_ATTRIBUTE = True


class PykormModel(ModelMixin):
    name: str = fields.Metadata('name', editable=False)
    created_at: str = fields.Metadata('creationTimestamp', editable=False)
    _k8s_uid: str = fields.Metadata('uid', editable=False)

    _pykorm_group: str
    _pykorm_version: str
    _pykorm_plural: str
    _pykorm_kind: str
    _property_fields: dict = {}
    _filter_labels: dict = {}

    _queryset: pykorm_query.BaseQuery

    @classmethod
    def process_labels(cls, d):
        return ','.join([f'{k}={v}' for k, v in d.items()])

    def to_dict(self):
        data = {}
        for attr_name, _ in self._get_attributes().items():
            v = getattr(self, attr_name)
            if v is None:
                continue
            if isinstance(_, fields.ListNestedField):
                data[attr_name] = [_.to_dict() for _ in list(v)]
            elif isinstance(_, fields.DictNestedField):
                data[attr_name] = v.to_dict()
            else:
                data[attr_name] = v
        for attr_name, attr_method in self._property_fields.items():
            data[attr_name] = getattr(self, attr_name)

        return {k: v for k, v in data.items() if not (k.startswith('_') and IGNORE_HIDDEN_ATTRIBUTE)}

    def _matches_attributes(self, filters_dict: Dict[str, str]) -> bool:
        for attribute_name, attribute_value in filters_dict.items():
            if getattr(self, attribute_name) != attribute_value:
                return False
        return True

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False

        return self._k8s_dict == other._k8s_dict

    @classmethod
    def _instantiate_with_dict(cls, k8s_dict, queryset) -> 'PykormModel':
        ''' Creates the model with data from the k8s data structure '''
        obj = cls.__new__(cls)
        obj._set_attributes_with_dict(k8s_dict)
        obj._queryset = queryset
        return obj

    def _cache_k8s_dict_snip(self, cache_key):  # minimize dict search scope
        if cache_key not in self._k8s_dict_cached:
            k8s_data = self.__k8s_data
            parent_key = self.get_parent_key(cache_key)  # if not found, try parent key
            if parent_key and parent_key in self._k8s_dict_cached:
                k8s_data = self._k8s_dict_cached[parent_key]
            d = dpath.util.get(k8s_data, cache_key, separator='@', default=None)
            cache_val = dpath.util.new({}, cache_key, d, separator='@')
            self._k8s_dict_cached[cache_key] = cache_val
        return self._k8s_dict_cached[cache_key]

    @staticmethod
    def get_parent_key(fullpath):
        paths = fullpath.split('@')
        if len(paths) > 1:
            parent_key = '@'.join(paths[:-1])
            return parent_key
        return fullpath

    def _set_attributes_with_dict(self, k8s_dict: Dict):
        self.__k8s_data = k8s_dict
        self._k8s_dict_cached = {}

        # list compression faster than for loop
        [setattr(self,
                 attr_name,
                 attr_value.get_data(self._cache_k8s_dict_snip(self.get_parent_key(attr_value.fullpath))))
         for attr_name, attr_value in self._get_attributes().items()]

    @property
    def _k8s_dict(self):
        '''
        Returns the model as a kubernetes dict/yaml structure
        '''
        if self._pykorm_group:
            api_version = f'{self._pykorm_group}/{self._pykorm_version}'
        else:
            api_version = self._pykorm_version

        d = {
            "apiVersion": api_version,
            "kind": self._pykorm_kind or self.__class__.__name__,
            "metadata": {
                "name": self.name,
            },
            # "spec": {
            # }
        }
        for attr_name, attr_type in self._get_attributes().items():
            attr_value = getattr(self, attr_name)
            if attr_type.required and not attr_value:
                raise Exception(f"Field {attr_name} must be set")
            if attr_type.readonly:  # Skip readonly field
                continue

            if isinstance(attr_type, fields.BaseNestedField) or (not isinstance(attr_value, fields.DataField)):
                attr_dict_path = attr_type.to_dict(attr_value)
                d = dpath.util.merge(attr_dict_path, d)
        return d

    def delete(self):
        return self._queryset._delete(self)

    def save(self):
        return self._queryset._save(self)

    def apply(self):
        return self._queryset._apply(self)


class NamespacedModel(PykormModel):
    namespace = fields.Metadata('namespace')


class ClusterModel(PykormModel):
    pass


class NestedField(ModelMixin):
    _root_dict_key = ''

    def to_dict(self):
        data = {}
        for attr_name, _ in self._get_attributes().items():
            v = getattr(self, attr_name)
            if isinstance(v, (NestedField, fields.DictNestedField)):
                v = v.to_dict()
            elif isinstance(_, fields.ListNestedField):
                v = [i.to_dict() for i in v or []]
            if v is not None:
                data[attr_name] = v
            else:
                data[attr_name] = None
        for attr_name, attr_method in self._property_fields.items():
            data[attr_name] = getattr(self, attr_name)
        return {k: v for k, v in data.items() if not (k.startswith('_') and IGNORE_HIDDEN_ATTRIBUTE)}

    def __eq__(self, other):
        return self.to_dict() == other
