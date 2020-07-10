import kubernetes

from . import query as pykorm_query
from . import models



def _process_cls(cls, query_class, group: str, version: str, plural: str):
    cls._pykorm_group = group
    cls._pykorm_version = version
    cls._pykorm_plural = plural
    cls.query = query_class(baseobject=cls)
    return cls


def k8s_custom_object(group: str, version: str, plural: str):
    def wrap(cls):
        if issubclass(cls, models.ClusterModel):
            query_class = pykorm_query.ClusterObjectQuery
        elif issubclass(cls, models.NamespacedModel):
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

    def save(self, obj: models.PykormModel):
        obj.query._save(obj)

    def delete(self, obj: models.PykormModel):
        obj.query._delete(obj)

