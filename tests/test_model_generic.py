import pytest
from conftest import Apple, Peach


def test_setattr_uid(pk):
    """ We shouldn't be able to set the model._k8s_uid attribute """
    a = Apple(name='a', variety='b')
    pk.save(a)

    with pytest.raises(Exception):
        a._k8s_uid = 'hello'


def test_model_compare_model(pk):
    a = Apple(name='name', variety='variety')
    peach = Peach(namespace='ns', name='name', variety='variety')

    assert a != peach


def test_model_compare_attrs(pk):
    a = Apple(name='a', variety='b')
    a_bis = Apple(name='a', variety='b')
    foreign = Apple(name='foreign', variety='foreign')

    assert a == a_bis
    assert a != foreign

    pk.save(a)
    assert list(Apple.query.all()) == [a]

    a.variety = 'not b'
    assert list(Apple.query.all()) != [a]

    pk.save(a)
    assert list(Apple.query.all()) == [a]
