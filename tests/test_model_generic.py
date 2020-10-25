import pytest
from conftest import Apple, Peach


def test_setattr_readonly(pk):
    """ We shouldn't be able to set the readonly attributes"""
    a = Apple(name='a', variety='b')
    pk.save(a)

    with pytest.raises(Exception):
        a._k8s_uid = 'hello'

    with pytest.raises(Exception):
        a.created_at = 'now'


def test_model_readonly_field(pk):
    a = Apple(name='a', variety='b')

    assert 'name' in a._k8s_dict['metadata']
    # However creationTimestamp is not because it's a readonly attr
    assert 'creationTimestamp' not in a._k8s_dict['metadata']


def test_model_setget_attr():
    a = Apple(name='name', variety='variety')
    assert a.variety == 'variety'

    a.variety = 'newvariety'

    assert a.variety == 'newvariety'

    a = Apple(name=None, variety=None)
    a.name = 'myapple'
    with pytest.raises(Exception):
        a.name = 'redefined-apple'


def test_model_setattr(pk):
    a = Peach(namespace='default', name='a', variety='b')

    assert a.variety == 'b'
    pk.save(a)

    a.variety = 'newb'
    pk.save(a)

    assert list(Peach.query.all()) == [a]
    assert a.variety == 'newb'


def test_model_k8s_dict(pk):
    a = Apple(name='a', variety='b', score={
        'exterior': 9
    })
    a_k8s_dict = a._k8s_dict

    expected_dict = {
        'metadata': {
            'name': 'a',
        },
        'spec': {
            'variety': 'b',
            'score': {
                'exterior': 9,
                'delicious': 10
            }
        },
    }

    assert expected_dict.items() <= a_k8s_dict.items()


def test_model_compare_model(pk):
    a = Apple(name='name', variety='variety')
    peach = Peach(namespace='default', name='name', variety='variety')

    assert a != peach


def test_model_compare_attrs(pk):
    a = Apple(name='a', variety='b')
    a_bis = Apple(name='a', variety='b')
    foreign = Apple(name='foreign', variety='foreign')

    assert a == a_bis
    assert a != foreign

    pk.save(a)
    assert list(Apple.query.all()) == list(Apple.query.all())

    assert list(Apple.query.all()) == [a]

    a.variety = 'not b'
    assert list(Apple.query.all()) != [a]

    pk.save(a)
    assert list(Apple.query.all()) == [a]
