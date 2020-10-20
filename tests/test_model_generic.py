import pytest
from conftest import Apple, Peach


def test_setattr_readonly(pk):
    """ We shouldn't be able to set the readonly attributes"""
    a = Apple('a', 'b')
    pk.save(a)
    print(a._k8s_dict)
    print(a._k8s_uid)
    print(a.creationTimestamp)

    with pytest.raises(Exception):
        a._k8s_uid = 'hello'

    with pytest.raises(Exception):
        a.creationTimestamp = 'now'


def test_model_readonly_field(pk):
    a = Apple(name='a', variety='b')

    assert 'name' in a._k8s_dict['metadata']
    # However creationTimestamp is not because it's a readonly attr
    assert 'creationTimestamp' not in a._k8s_dict['metadata']


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

