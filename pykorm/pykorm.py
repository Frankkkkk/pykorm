import inspect

import kubernetes

from . import query as pykorm_query
from . import fields



class PykormModel:
    name: str = fields.Metadata('name')

    _k8s_uid = None
    _pykorm_group: str = None
    _pykorm_version: str = None
    _pykorm_plural: str = None

    query: pykorm_query.BaseQuery = None

    @classmethod
    def _instantiate_with_dict(cls, k8s_dict):
        obj = cls()
        obj.__k8s_data = k8s_dict

        attributes = inspect.getmembers(cls, lambda a:not(inspect.isroutine(a)))
        obj_attrs = [a for a in attributes if not(a[0].startswith('__') and a[0].endswith('__'))]

        for (attr_name, attr_value) in obj_attrs:
            if isinstance(attr_value, fields.DataField):
                print(f'{attr_name} is a field !!')
                value = attr_value.get_data(k8s_dict)
                obj.__dict__[attr_name] = value
        # XXX TODO: fill attributes of obj with k8s dict
        return obj


class NamespacedModel(PykormModel):
    namespace: str = None


class ClusterModel(PykormModel):
    pass


def _process_cls(cls, query_class, group: str, version: str, plural: str):
    cls._pykorm_group = group
    cls._pykorm_version = version
    cls._pykorm_plural = plural
    cls.query = query_class(baseobject=cls)
    return cls


def k8s_custom_object(group: str, version: str, plural: str):
    def wrap(cls):
        if issubclass(cls, ClusterModel):
            query_class = pykorm_query.ClusterObjectQuery
        elif issubclass(cls, NamespacedModel):
            query_class = pykorm_query.NamespacedObjectQuery
        else:
            raise Exception(f"Class {cls} doesn't seem to inherit from either ClusterModel nor NamespacedModel")

        return _process_cls(cls, query_class, group, version, plural)

    return wrap



class Pykorm:
    def __init__(self):
        # To be changed once https://github.com/kubernetes-client/python/issues/1005 is fixed
        try:
            kubernetes.config.load_kube_config()
        except:  # XXX
            kubernetes.config.load_incluster_config()






@k8s_custom_object(group='group', version='version', plural='plural')
class MyDB(NamespacedModel):
    def quack(self):
        print('Quack !')
