import inspect
import json
import re
from typing import TYPE_CHECKING, Iterator

import kubernetes
from kubernetes.client.rest import ApiException

from pykorm.pykorm import Pykorm

if TYPE_CHECKING:
    from .models import PykormModel, NamespacedModel, ClusterModel


class Filter:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class Node(object):
    def clone(self):
        obj = self.__class__.__new__(self.__class__)
        obj.__dict__ = self.__dict__.copy()
        # We also copy the following attrs in order to not_impact other instances
        obj._next_filter = obj._next_filter.copy()
        obj._label_filters = obj._label_filters.copy()
        obj._field_filters = obj._field_filters.copy()

        return obj

    @staticmethod
    def copy(method):
        def inner(self, *args, **kwargs):
            clone = self.clone()
            method(clone, *args, **kwargs)
            return clone

        return inner


class BaseQuery(Node):
    baseobject: 'PykormModel'

    def __init__(self, baseobject: 'PykormModel', api):
        self.baseobject = baseobject
        self._next_filter = []
        self._label_filters = {}
        self._field_filters = {}
        self._api = api
        self._current_cluster = 'default'
        self._overwrite_api_client = None
        self._overwrite_api_client_mapping = {}

    @property
    def api_client_mapping(self):
        if self._overwrite_api_client_mapping:
            return self._overwrite_api_client_mapping
        return Pykorm.get_api_client_mapping()

    def _reset_api_client(self):
        self._api.api_client = self.api_client

    @Node.copy
    def overwrite_clusters(self, clusters_config):
        self._overwrite_api_client_mapping = Pykorm.get_api_client_mapping(clusters_config)
        self._reset_api_client()

    @property
    def api_client(self):
        if self._overwrite_api_client:
            return self._overwrite_api_client
        return self.api_client_mapping[self._current_cluster]

    @property
    def api(self):
        if inspect.isclass(self._api):
            self._api = self._api(self.api_client)
        return self._api

    @property
    def is_crd(self):
        return isinstance(self.api, kubernetes.client.CustomObjectsApi)

    def __call__(self, *args, **kwargs):
        if 'overwrite_api_client' in kwargs:
            self._overwrite_api_client = kwargs['overwrite_api_client']
            self._reset_api_client()
        return self.__class__(self.baseobject, self.api)

    @property
    def api_resource_name(self):
        if self.is_crd:
            return 'custom_object'
        found = re.findall('[A-Z][^A-Z]*', self.baseobject._pykorm_kind)
        return '_'.join([_.lower() for _ in found])

    def process_method_kwargs(self, obj: 'PykormModel', with_labels=False, **kwargs):
        from .models import NamespacedModel
        ret = kwargs

        if isinstance(obj, NamespacedModel):
            ret['namespace'] = obj.namespace

        if self.is_crd:
            ret.update({
                'group': obj._pykorm_group,
                'version': obj._pykorm_version,
                'plural': obj._pykorm_plural,
            })
        if with_labels:
            labels = {}
            labels.update(self._label_filters)  # from query
            ret['label_selector'] = obj.process_labels(labels)

            fields = self._field_filters
            ret['field_selector'] = obj.process_labels(fields)

        ret['_preload_content'] = False
        ret['_request_timeout'] = (2, 5)
        return ret

    @Node.copy
    def filter_by(self, **kwargs: str):
        self._next_filter.append(Filter(**kwargs))

    @Node.copy
    def filter_by_labels(self, **kwargs):
        self._label_filters.update(kwargs)

    @Node.copy
    def filter_by_fields(self, **kwargs):
        self._field_filters.update(kwargs)

    @Node.copy
    def using(self, cluster='default'):
        self._current_cluster = cluster
        self._reset_api_client()

    def _query(self, data=None, **kwargs):
        ret = []
        if data is None:
            data = self._iter(**kwargs)
        for el in data:
            if el._matches_attributes(kwargs):
                ret.append(el)
        return ret

    def all(self) -> ['PykormModel']:
        last_ret = None
        if not self._next_filter:
            return self._query()
        for _filter in self._next_filter:
            last_ret = self._query(data=last_ret, **_filter.kwargs)
        return last_ret

    def first(self):
        _all = self.all()
        if _all:
            return _all[0]

    def get(self, name):
        all_kwargs = {}
        [all_kwargs.update(f.kwargs) for f in self._next_filter]
        namespace = all_kwargs.get('namespace')
        if not namespace:
            raise Exception('Must specify namespace')
        return self._get(namespace, name)

    def _save(self, obj: 'PykormModel'):
        k8s_dict = obj._k8s_dict

        kwargs = self.process_method_kwargs(obj, body=k8s_dict)

        if obj._k8s_uid is None:
            result = self.create_method(**kwargs)
        else:
            kwargs['name'] = obj.name
            result = self.patch_method(**kwargs)

        obj._set_attributes_with_dict(self.process_http_response(result))
        obj._queryset = self

    def _apply(self, obj: 'PykormModel'):
        k8s_dict = obj._k8s_dict

        try:
            result = self.create_method(**self.process_method_kwargs(obj, body=k8s_dict))
        except ApiException as e:
            if e.status == 409:
                result = self.patch_method(name=obj.name, **self.process_method_kwargs(obj, body=k8s_dict))

        obj._set_attributes_with_dict(self.process_http_response(result))

    @staticmethod
    def process_http_response(http_response):
        return json.loads(http_response.read())


class NamespacedObjectQuery(BaseQuery):
    def _iter(self, **kwargs) -> Iterator['NamespacedModel']:
        base_cls = self.baseobject
        namespace = kwargs.get('namespace', None)
        method = self.list_method
        method_kwargs = self.process_method_kwargs(base_cls, with_labels=True, namespace=namespace)

        # No namespace, no problem. Search cluster wide.
        if not namespace:
            method = self.list_method_cluster
            del method_kwargs['namespace']  # Clean up needed to avoid an API error

        objs = self.process_http_response(method(**method_kwargs))
        for obj in objs['items']:
            yield self.baseobject._instantiate_with_dict(obj, queryset=self)

    @property
    def get_method(self):
        if self.is_crd:
            return getattr(self.api, f'get_namespaced_{self.api_resource_name}')
        return getattr(self.api, f'read_namespaced_{self.api_resource_name}')

    @property
    def list_method(self):
        return getattr(self.api, f'list_namespaced_{self.api_resource_name}')

    @property
    def list_method_cluster(self):
        if self.is_crd:
            return getattr(self.api, f'list_cluster_{self.api_resource_name}')
        return getattr(self.api, f'list_{self.api_resource_name}_for_all_namespaces')

    @property
    def patch_method(self):
        return getattr(self.api, f'patch_namespaced_{self.api_resource_name}')

    @property
    def create_method(self):
        return getattr(self.api, f'create_namespaced_{self.api_resource_name}')

    @property
    def delete_method(self):
        return getattr(self.api, f'delete_namespaced_{self.api_resource_name}')

    def _get(self, namespace, name):
        try:
            result = self.get_method(
                **self.process_method_kwargs(self.baseobject, namespace=namespace, name=name)
            )
        except ApiException as e:
            if e.status == 404:
                return
            else:
                raise Exception
        if result:
            obj = self.process_http_response(result)
            return self.baseobject._instantiate_with_dict(obj, queryset=self)

    def _delete(self, obj: 'NamespacedModel'):
        self.delete_method(**self.process_method_kwargs(obj, namespace=obj.namespace, name=obj.name))


class ClusterObjectQuery(BaseQuery):
    @property
    def get_method(self):
        if self.is_crd:
            return self.api.get_cluster_custom_object
        return getattr(self.api, f'get_{self.api_resource_name}')

    @property
    def list_method(self):
        if self.is_crd:
            return self.api.list_cluster_custom_object
        return getattr(self.api, f'list_{self.api_resource_name}')

    @property
    def patch_method(self):
        if self.is_crd:
            return self.api.patch_cluster_custom_object
        return getattr(self.api, f'patch_{self.api_resource_name}')

    @property
    def create_method(self):
        if self.is_crd:
            return self.api.create_cluster_custom_object
        return getattr(self.api, f'create_{self.api_resource_name}')

    @property
    def delete_method(self):
        if self.is_crd:
            return self.api.delete_cluster_custom_object
        return getattr(self.api, f'delete_{self.api_resource_name}')

    def _iter(self, **kwargs) -> Iterator['ClusterModel']:
        base_cls = self.baseobject
        objs = self.process_http_response(self.list_method(**self.process_method_kwargs(base_cls, with_labels=True)))
        for obj in objs['items']:
            yield self.baseobject._instantiate_with_dict(obj, queryset=self)

    def _delete(self, obj: 'ClusterModel'):
        self.delete_method(**self.process_method_kwargs(obj, name=obj.name))

    def get(self, name):
        return self._get(name)

    def _get(self, name):
        try:
            result = self.get_method(**self.process_method_kwargs(self.baseobject, name=name))
        except ApiException as e:
            if e.status == 404:
                return
        if result:
            obj = self.process_http_response(result)
            return self.baseobject._instantiate_with_dict(obj, queryset=self)
