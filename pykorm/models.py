import inspect
from typing import List, Tuple

from . import fields
from . import query as pykorm_query


def dict_deep_merge(source, destination):
    """
    run me with nosetests --with-doctest file.py

    >>> a = { 'first' : { 'all_rows' : { 'pass' : 'dog', 'number' : '1' } } }
    >>> b = { 'first' : { 'all_rows' : { 'fail' : 'cat', 'number' : '5' } } }
    >>> merge(b, a) == { 'first' : { 'all_rows' : { 'pass' : 'dog', 'fail' : 'cat', 'number' : '5' } } }
    True
    """
    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            dict_deep_merge(value, node)
        else:
            destination[key] = value

    return destination




class PykormModel:
    name: str = fields.Metadata('name')

    _k8s_uid = None
    _pykorm_group: str = None
    _pykorm_version: str = None
    _pykorm_plural: str = None

    query: pykorm_query.BaseQuery = None

    @classmethod
    def _get_pykorm_attributes(cls) -> List[Tuple[str, fields.DataField]]:
        attributes = inspect.getmembers(cls, lambda a:not(inspect.isroutine(a)))
        obj_attrs = [a for a in attributes if not(a[0].startswith('__') and a[0].endswith('__'))]

        retl = []
        for obj in obj_attrs:
            (_attr_name, attr_value) = obj
            if isinstance(attr_value, fields.DataField):
                retl.append(obj)
        return retl


    @classmethod
    def _instantiate_with_dict(cls, k8s_dict):
        ''' Creates the model with data from the k8s data structure '''
        obj = cls.__new__(cls)
        obj.__k8s_data = k8s_dict

        for (attr_name, attr_value) in cls._get_pykorm_attributes():
            print(f'{attr_name} is a field !!')
            value = attr_value.get_data(k8s_dict)
            obj.__dict__[attr_name] = value
        return obj


    @property
    def _k8s_dict(self):
        d = {
            "apiVersion": f'{self._pykorm_group}/{self._pykorm_version}',
            "kind": self.__class__.__name__,
            "metadata": {
                "name": self.name,
            },
            "spec": {
            }
        }

        for (attr_name, attr_type) in self._get_pykorm_attributes():
            attr_value = getattr(self, attr_name)
            attr_dict_path = attr_type.as_k8s_path(attr_value)
            print(f'I also have {attr_name}→{attr_value} = {attr_type}')
            print(attr_dict_path)
            d = dict_deep_merge(d, attr_dict_path)
        return d

class NamespacedModel(PykormModel):
    namespace: str = fields.Metadata('namespace')

    @property
    def _k8s_dict(self):
        d = super(PykormModel, self).__k8s_dict
        d['metadata']['namespace'] = self.namespace


class ClusterModel(PykormModel):
    pass

