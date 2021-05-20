from conftest import Pod


def test_read():
    Pod.query.all()
