import kubernetes

from . import models
from . import query as pykorm_query


def _process_cls(cls, query_class, group: str, version: str, plural: str, api,
                 kind: str = None):
    cls._pykorm_group = group
    cls._pykorm_version = version
    cls._pykorm_plural = plural
    cls._pykorm_kind = kind
    cls.query = query_class(baseobject=cls, api=api)()
    return cls


def get_query_cls(cls):
    if issubclass(cls, models.ClusterModel):
        return pykorm_query.ClusterObjectQuery
    elif issubclass(cls, models.NamespacedModel):
        return pykorm_query.NamespacedObjectQuery
    else:
        raise Exception(f"Class {cls} doesn't seem to inherit from either ClusterModel nor NamespacedModel")


def k8s_custom_object(group: str, version: str, plural: str, kind: str = None):
    def wrap(cls):
        query_class = get_query_cls(cls)
        return _process_cls(cls, query_class, group, version, plural, api=kubernetes.client.CustomObjectsApi, kind=kind)

    return wrap


def k8s_core(kind: str):
    def wrap(cls):
        query_class = get_query_cls(cls)
        return _process_cls(cls, query_class, group=None, version='v1', plural=None, api=kubernetes.client.CoreV1Api,
                            kind=kind)

    return wrap


def k8s_appsv1(kind: str):
    def wrap(cls):
        query_class = get_query_cls(cls)
        return _process_cls(cls, query_class, group='apps', version='v1', plural=None,
                            api=kubernetes.client.AppsV1Api,
                            kind=kind)

    return wrap


class Pykorm:
    clusters_config = {}  # define api configuration

    @classmethod
    def get_api_client_mapping(cls, clusters_config=None):
        if clusters_config is None:  # allow overwrite global clusters config
            clusters_config = cls.clusters_config

        api_client_mapping = {}  # store api client mapping


        # Load the `default` cluster from kubeconfig/incluster config
        try:
            # To be changed once https://github.com/kubernetes-client/python/issues/1005 is fixed
            kubernetes.config.load_kube_config()
        except kubernetes.config.config_exception.ConfigException:
            try:
                kubernetes.config.load_incluster_config()
            except:
                # Not a problem for now a users can later specify a custom kubeconfig
                # with pykorm.Pykorm.clusters_config = dict[cluster_name, kubeconfig]
                pass

        api_client = kubernetes.client.ApiClient()
        api_client_mapping['default'] = api_client

        # Load other cluster if specified in configuration
        if clusters_config:
            for cluster_name, api_config in clusters_config.items():
                if isinstance(api_config, kubernetes.client.Configuration):
                    configuration = api_config
                else:
                    configuration = kubernetes.client.Configuration()
                    for k, v in api_config.items():
                        setattr(configuration, k, v)

                api_client_mapping[cluster_name] = kubernetes.client.ApiClient(configuration)
        return api_client_mapping

    def save(self, obj: 'models.PykormModel', cluster: str = 'default'):
        obj.query().using(cluster)._save(obj)

    def delete(self, obj: 'models.PykormModel', cluster: str = 'default'):
        obj.query().using(cluster)._delete(obj)

    def apply(self, obj: 'models.PykormModel', cluster: str = 'default'):
        raise Exception('Please use save() instead')
