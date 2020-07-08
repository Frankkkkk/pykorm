import time

import kubernetes

import pykorm


@pykorm.k8s_custom_object('pykorm.infomaniak.com', 'v1', 'apples')
class Apple(pykorm.ClusterModel):
    variety: str = pykorm.fields.Spec('variety')
    time_bought: str #= pykorm.fields.Metadata('.annotations.bought_at')


def test_empty():

    pykorm.Pykorm()

    assert len(list(Apple.query.all())) == 0

def test_read():
    apple_js = {
        "apiVersion": "pykorm.infomaniak.com/v1",
        "kind": "Apple",
        "metadata": {
            "name": "good-apple",
        },
        "spec": {
            "variety": "Gala",
        }
    }
    api = kubernetes.client.CustomObjectsApi()
    try:
        api.create_cluster_custom_object('pykorm.infomaniak.com', 'v1', 'apples', apple_js)
    except:
        pass

    all_apples = list(Apple.query.all())

    assert len(all_apples) == 1
    apple = all_apples[0]

    assert apple.variety == 'Gala'

#apple = Apple('Gala', time.time())
#pk.save(apple)