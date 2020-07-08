import time

import kubernetes
import pytest

import pykorm


@pykorm.k8s_custom_object('pykorm.infomaniak.com', 'v1', 'apples')
class Apple(pykorm.ClusterModel):
    variety: str = pykorm.fields.Spec('variety')
    time_bought: str #= pykorm.fields.Metadata('.annotations.bought_at')


@pytest.fixture
def remove_all_apples(custom_objects_api):
    def do_remove(custom_objects_api):
        apples = custom_objects_api.list_cluster_custom_object('pykorm.infomaniak.com', 'v1', 'apples')
        for apple in apples['items']:
            print(f'Will remove {apple}')
            custom_objects_api.delete_cluster_custom_object('pykorm.infomaniak.com', 'v1', 'apples', apple['metadata']['name'])

    do_remove(custom_objects_api)
    yield None
    do_remove(custom_objects_api)




def test_empty(remove_all_apples, pk):
    assert len(list(Apple.query.all())) == 0


def test_read(custom_objects_api, remove_all_apples):
    apple_js = {
        "apiVersion": "pykorm.infomaniak.com/v1",
        "kind": "Apple",
        "metadata": {
            "name": "tasty-apple",
        },
        "spec": {
            "variety": "Gala",
        }
    }
    custom_objects_api.create_cluster_custom_object('pykorm.infomaniak.com', 'v1', 'apples', apple_js)

    all_apples = list(Apple.query.all())

    assert len(all_apples) == 1
    apple = all_apples[0]

    assert apple.name == 'tasty-apple'
    assert apple.variety == 'Gala'


def test_create(pk):
    cake_apple = Apple(name='cake-apple', variety='Golden')

    pk.save(cake_apple)

    pass

#apple = Apple('Gala', time.time())
#pk.save(apple)