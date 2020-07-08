import abc
import kubernetes

def _custom_objects_api():
    return kubernetes.client.CustomObjectsApi()

class BaseQuery:
    baseobject: type = None

    def __init__(self, baseobject: type):
        self.baseobject = baseobject

    @abc.abstractmethod
    def _iter(self):
        raise Exception('Not implemented')

    def all(self):
        for el in self._iter():
            yield el



class NamespacedObjectQuery(BaseQuery):
    pass


class ClusterObjectQuery(BaseQuery):
    def _iter(self):
        api = _custom_objects_api()
        base_cls = self.baseobject

        objs = api.list_cluster_custom_object(base_cls._pykorm_group, base_cls._pykorm_version, base_cls._pykorm_plural)
        for obj in objs['items']:
            yield self.baseobject._instantiate_with_dict(obj)

