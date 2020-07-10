import inspect

from . import fields
from . import query as pykorm_query

class PykormModel:
    name: str = fields.Metadata('name')

    _k8s_uid = None
    _pykorm_group: str = None
    _pykorm_version: str = None
    _pykorm_plural: str = None

    query: pykorm_query.BaseQuery = None

    @classmethod
    def _instantiate_with_dict(cls, k8s_dict):
        ''' Creates the model with data from the k8s data structure '''
        obj = cls.__new__(cls)
        obj.__k8s_data = k8s_dict

        attributes = inspect.getmembers(cls, lambda a:not(inspect.isroutine(a)))
        obj_attrs = [a for a in attributes if not(a[0].startswith('__') and a[0].endswith('__'))]

        for (attr_name, attr_value) in obj_attrs:
            if isinstance(attr_value, fields.DataField):
                print(f'{attr_name} is a field !!')
                value = attr_value.get_data(k8s_dict)
                obj.__dict__[attr_name] = value
        return obj


class NamespacedModel(PykormModel):
    namespace: str = None


class ClusterModel(PykormModel):
    pass

