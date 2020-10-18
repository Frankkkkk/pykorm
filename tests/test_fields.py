from conftest import Score

from pykorm import fields


def test_nested_field_to_dict():
    md = fields.DictNestedField(Score, path='spec@score')
    wanted = {
        'spec': {
            'score': {
                'delicious': 10
            }
        }
    }
    assert md.to_dict(Score(delicious=10)) == wanted


def test_nested_field_get_data():
    md = fields.DictNestedField(Score, path='spec@score')

    wanted = Score(delicious=10)
    k8s_js = {
        'spec': {
            'score': {
                'delicious': 10
            }
        }
    }

    assert md.get_data(k8s_js) == wanted


def test_nested_field_get_data_default():
    md = fields.DictNestedField(Score, path='spec@score')

    k8s_js = {
        'spec': {
            'score': {
            }
        }
    }

    assert md.get_data(k8s_js).delicious == 10


def test_metadata_to_dict():
    md = fields.Metadata('hello@foo@bar')
    wanted = {
        'metadata': {
            'hello': {
                'foo': {
                    'bar': '42'
                }
            }
        }
    }

    assert md.to_dict('42') == wanted


def test_metadata_get_data():
    md = fields.Metadata('annotations@foo@bar')

    wanted = 'YEAHMAN'
    k8s_js = {
        'spec': {
            'random': 'true',
        },
        'metadata': {
            'useless': 'yes',
            'annotations': {
                'this-is-getting': 'tiresome',
                'foo': {
                    'last': 'one',
                    'bar': wanted,
                }
            }
        }
    }

    assert md.get_data(k8s_js) == wanted


def test_metadata_get_data_default():
    md = fields.Metadata('annotations@default', 'yeah')

    k8s_js = {
        'spec': {
            'random': 'true',
        },
        'metadata': {
            'useless': 'yes',
        }
    }

    assert md.get_data(k8s_js) == 'yeah'

    k8s_js['metadata']['annotations'] = {'default': 'works'}
    assert md.get_data(k8s_js) == 'works'


def test_metadata_annotations_field():
    md = fields.MetadataAnnotation('ch.infomaniak.pykorm/foo.bar')

    k8s_js = {
        'spec': {
            'random': 'true',
        },
        'metadata': {
            'annotations': {
                'ch.infomaniak.pykorm/foo.bar': 'baz'
            }
        }
    }

    assert md.get_data(k8s_js) == 'baz'


def test_metadata_annotations_field_default():
    md = fields.MetadataAnnotation('ch.infomaniak.pykorm/foo.bar', 'default')
    assert md.get_data({}) == 'default'
