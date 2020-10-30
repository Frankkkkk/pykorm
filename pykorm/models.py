from typing import Dict

import dpath.util

from . import fields
from . import query as pykorm_query
from .meta import ModelMixin


class PykormModel(ModelMixin):
    name: str = fields.Metadata('name', readonly=True)
    created_at: str = fields.Metadata('creationTimestamp', readonly=True)
    _k8s_uid: str = fields.Metadata('uid', readonly=True)

    _pykorm_group: str
    _pykorm_version: str
    _pykorm_plural: str
    _pykorm_kind: str
    _property_fields: dict = {}

    _queryset: pykorm_query.BaseQuery

    @classmethod
    def process_labels(cls, d: Dict[str, str]) -> str:
        ''' Converts a labels_dict to a k=v,k=v string '''
        return ','.join([f'{k}={v}' for k, v in d.items()])

    def _matches_attributes(self, filters_dict: Dict[str, str]) -> bool:
        for attribute_name, attribute_value in filters_dict.items():
            if getattr(self, attribute_name) != attribute_value:
                return False
        return True

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        return self._k8s_dict == other._k8s_dict

    def __hash__(self):
        return hash(self._k8s_uid)

    @classmethod
    def _instantiate_with_dict(cls, k8s_dict, queryset) -> 'PykormModel':
        ''' Creates the model with data from the k8s data structure '''
        obj = cls.__new__(cls)
        obj._set_attributes_with_dict(k8s_dict)
        obj._queryset = queryset
        return obj

    def _set_attributes_with_dict(self, k8s_dict: Dict):
        self.__k8s_data = k8s_dict
        self._k8s_dict_cached = {}

        for (attr_name, attr) in self._get_attributes().items():
            value = attr.get_data(k8s_dict)
            self.__dict__[attr_name] = value

    @property
    def _k8s_dict(self):
        '''
        Returns the model as a kubernetes dict/yaml structure. This function
        does NOT return readonly fields
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
        }

        for (attr_name, attr_type) in self._get_attributes().items():
            attr_value = getattr(self, attr_name)

            if attr_type.required and not attr_value:
                raise Exception(f"Field {attr_name} must be set")

            if attr_type.readonly:  # Skip readonly field
                continue

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


class Nested(ModelMixin):
    pass
