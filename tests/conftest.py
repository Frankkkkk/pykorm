import uuid

import kubernetes
import pytest

import pykorm


class Score(pykorm.models.Nested):
    exterior: int = pykorm.fields.DataField('exterior')
    delicious: int = pykorm.fields.DataField('delicious', 10)


class ScoreMixin(object):
    score: Score = pykorm.fields.DictNestedField(Score, path=['spec', 'score'])


@pykorm.k8s_custom_object('pykorm.infomaniak.com', 'v1', 'apples')
class Apple(ScoreMixin, pykorm.ClusterModel):
    variety: str = pykorm.fields.Spec('variety', 'default-variety')
    price: str = pykorm.fields.Spec('price', 1)


@pykorm.k8s_custom_object('pykorm.infomaniak.com', 'v1', 'peaches')
class Peach(ScoreMixin, pykorm.NamespacedModel):
    variety: str = pykorm.fields.Spec('variety', 'default-variety')
    price: str = pykorm.fields.Spec('price', 1)


@pytest.fixture
def random_name():
    return uuid.uuid4().hex


@pytest.fixture
def custom_objects_api():
    kubernetes.config.load_kube_config()
    return kubernetes.client.CustomObjectsApi()


@pytest.fixture
def pk():
    return pykorm.Pykorm()


def remove_all_apples(custom_objects_api):
    apples = custom_objects_api.list_cluster_custom_object('pykorm.infomaniak.com', 'v1', 'apples')
    for apple in apples['items']:
        custom_objects_api.delete_cluster_custom_object('pykorm.infomaniak.com', 'v1', 'apples',
                                                        apple['metadata']['name'])


def remove_all_peaches(custom_objects_api):
    corev1 = kubernetes.client.CoreV1Api()
    ns = corev1.list_namespace()
    for ns in ns.items:
        ns_name = ns.metadata.name
        peaches = custom_objects_api.list_namespaced_custom_object('pykorm.infomaniak.com', 'v1', ns_name, 'peaches')
        for peach in peaches['items']:
            custom_objects_api.delete_namespaced_custom_object('pykorm.infomaniak.com', 'v1', ns_name, 'peaches',
                                                               peach['metadata']['name'])


@pytest.fixture(autouse=True, scope='function')
def remove_all_CR(custom_objects_api):
    remove_all_apples(custom_objects_api)
    remove_all_peaches(custom_objects_api)
