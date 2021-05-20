from conftest import Namespace


def test_read():
    Namespace.query.all()
