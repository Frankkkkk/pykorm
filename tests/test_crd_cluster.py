import time

import kubernetes
import pytest

from conftest import Apple



def test_empty():
    assert len(list(Apple.query.all())) == 0


def test_read(custom_objects_api):
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

    all_apples = Apple.query.all()
    assert [cake_apple] == list(all_apples)


def test_update(pk):
    a = Apple('rotten', 'Cameo')
    pk.save(a)

    a.variety = 'Old Cameo'
    pk.save(a)


    all_apples = Apple.query.all()
    assert [a] == list(all_apples)



def test_delete(pk):
    a = Apple('a', 'b')
    pk.save(a)
    pk.delete(a)

    assert list(Apple.query.all()) == []
