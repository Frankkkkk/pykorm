import time

import kubernetes
import pytest

from conftest import Peach


def test_empty(pk):
    assert len(list(Peach.query.all())) == 0


def test_read(custom_objects_api):
    apple_js = {
        "apiVersion": "pykorm.infomaniak.com/v1",
        "kind": "Peach",
        "metadata": {
            "namespace": "default",
            "name": "tasty-peach",
        },
        "spec": {
            "variety": "Riga",
        }
    }
    custom_objects_api.create_namespaced_custom_object('pykorm.infomaniak.com', 'v1', 'default', 'peaches', apple_js)

    all_peaches = list(Peach.query.all())

    assert len(all_peaches) == 1
    peach = all_peaches[0]

    assert peach.name == 'tasty-peach'
    assert peach.variety == 'Riga'


def test_create(pk):
    cake_peach = Peach(namespace='default', name='cake-peach', variety='Frost')  # 😱
    pk.save(cake_peach)

    all_peaches = Peach.query.all()
    assert [cake_peach] == list(all_peaches)


def test_update(pk):
    a = Peach(namespace='default', name='rotten', variety='Red Heaven')
    pk.save(a)

    a.variety = 'Blue Heaven'
    pk.save(a)


    all_peaches = Peach.query.all()
    assert [a] == list(all_peaches)



def test_delete(pk):
    a = Peach(namespace='default', name='a', variety='b')
    pk.save(a)
    pk.delete(a)

    assert list(Peach.query.all()) == []


# XXX test raises when no namespace