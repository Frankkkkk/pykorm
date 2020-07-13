from typing import TYPE_CHECKING, Iterator

import kubernetes

if TYPE_CHECKING:
    from .models import PykormModel, NamespacedModel, ClusterModel



def _custom_objects_api():
    return kubernetes.client.CustomObjectsApi()


def _coreV1_api():
    return kubernetes.client.CoreV1Api()


class BaseQuery:
    baseobject: 'PykormModel'

    def __init__(self, baseobject: 'PykormModel'):
        self.baseobject = baseobject

    def filter_by(self, **kwargs: str) -> Iterator['PykormModel']:
        for el in self._iter():
            if el._matches_attributes(kwargs):
                yield el


    def all(self) -> Iterator['PykormModel']:
        for el in self._iter():
            yield el



class NamespacedObjectQuery(BaseQuery):
    def _iter(self) -> Iterator['NamespacedModel']:
        api = _custom_objects_api()
        corev1 = _coreV1_api()
        base_cls = self.baseobject


        for namespace in corev1.list_namespace().items:
            ns_name = namespace.metadata.name
            objs = api.list_namespaced_custom_object(base_cls._pykorm_group, base_cls._pykorm_version, ns_name, base_cls._pykorm_plural)
            for obj in objs['items']:
                yield self.baseobject._instantiate_with_dict(obj)


    def _save(self, obj: 'NamespacedModel'):
        api = _custom_objects_api()

        k8s_dict = obj._k8s_dict

        if obj._k8s_uid is None:
            result = api.create_namespaced_custom_object(obj._pykorm_group, obj._pykorm_version, obj.namespace, obj._pykorm_plural, k8s_dict)
        else:
            result = api.patch_namespaced_custom_object(obj._pykorm_group, obj._pykorm_version, obj.namespace, obj._pykorm_plural, obj.name, k8s_dict)

        obj._set_attributes_with_dict(result)


    def _delete(self, obj: 'NamespacedModel'):
        api = _custom_objects_api()
        api.delete_namespaced_custom_object(obj._pykorm_group, obj._pykorm_version, obj.namespace, obj._pykorm_plural, obj.name)



class ClusterObjectQuery(BaseQuery):
    def _iter(self) -> Iterator['ClusterModel']:
        api = _custom_objects_api()
        base_cls = self.baseobject

        objs = api.list_cluster_custom_object(base_cls._pykorm_group, base_cls._pykorm_version, base_cls._pykorm_plural)
        for obj in objs['items']:
            yield self.baseobject._instantiate_with_dict(obj)


    def _save(self, obj: 'ClusterModel'):
        api = _custom_objects_api()

        k8s_dict = obj._k8s_dict

        if obj._k8s_uid is None:
            result = api.create_cluster_custom_object(obj._pykorm_group, obj._pykorm_version, obj._pykorm_plural, k8s_dict)
        else:
            result = api.patch_cluster_custom_object(obj._pykorm_group, obj._pykorm_version, obj._pykorm_plural, obj.name, k8s_dict)

        obj._set_attributes_with_dict(result)


    def _delete(self, obj: 'ClusterModel'):
        api = _custom_objects_api()
        api.delete_cluster_custom_object(obj._pykorm_group, obj._pykorm_version, obj._pykorm_plural, obj.name)


