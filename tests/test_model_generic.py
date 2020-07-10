import pytest
from conftest import Apple


def test_setattr_uid(pk):
    """ We shouldn't be able to set the model._k8s_uid attribute """
    a = Apple('a', 'b')
    pk.save(a)

    with pytest.raises(Exception):
        a._k8s_uid = 'hello'