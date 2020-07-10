import uuid

import kubernetes
import pytest

import pykorm

@pytest.fixture
def random_name():
    return uuid.uuid4().hex

@pytest.fixture
def custom_objects_api():
    kubernetes.config.load_kube_config()
    return kubernetes.client.CustomObjectsApi()


@pytest.fixture
def pk():
    return pykorm.Pykorm()