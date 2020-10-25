from pykorm import fields
from pykorm.models import Nested


def test_nested_to_dict():
    class TestObject(Nested):
        foo = fields.DataField('foo')
        bar = fields.DataField('bar')
        foobar = fields.DataField('foobar', default='foobar')
        foobarfoo = fields.DataField('foobarfoo', allow_empty=True)
        foobarfoobar = fields.DataField('foobarfoobar')
        foobarfoobarfoobar = fields.DataField(['foobarfoobarfoobar', 'foobarfoobarfoobar'])

    ed = fields.DictNestedField(
        TestObject, path='obj'
    )

    eds = fields.ListField(TestObject, path='objs')

    wanted1 = {
        'obj': {
            'foo': 'foo',
            'bar': 'bar',
            'foobar': 'foobar',
            'foobarfoo': None,
            'foobarfoobarfoobar': {
                'foobarfoobarfoobar': 'foobarfoobarfoobar'
            }
        }
    }
    wanted2 = {
        'objs': [
            {
                'foo': 'foo1',
                'bar': 'bar1',
                'foobar': 'foobar',
                'foobarfoo': None
            },
            {
                'foo': 'foo2',
                'bar': 'bar2',
                'foobar': 'foobar',
                'foobarfoo': None
            },
        ]
    }
    ed_dict = ed.to_dict(TestObject(foo='foo', bar='bar', foobarfoobarfoobar='foobarfoobarfoobar'))
    assert ed_dict == wanted1
    assert 'foobarfoobar' not in wanted1['obj']
    eds_dict = eds.to_dict([TestObject(foo='foo1', bar='bar1'), TestObject(foo='foo2', bar='bar2')])
    assert eds_dict == wanted2
    for item in eds_dict['objs']:
        assert 'foobarfoobar' not in item


def test_nested_get_data():
    class DoubleNested(Nested):
        foo = fields.DataField('foo')
        bar = fields.DataField('bar')
        foobar = fields.DataField('foobar', default='foobar')

    class OneNested(Nested):
        foo = fields.DataField('foo')
        bar = fields.DataField('bar')
        double_nested = fields.DictNestedField(DoubleNested, path='double_nested')

    ed = fields.ListField(
        OneNested, path=['spec', 'one_nested_list']
    )

    k8s_js = {
        'spec': {
            'one_nested_list': [
                {
                    'foo': 'foo',
                    'bar': 'bar',
                    'double_nested': {
                        'foo': 'foo',
                    }
                }
            ]
        }
    }

    assert ed.get_data(k8s_js)[0].foo == 'foo'
    assert ed.get_data(k8s_js)[0].bar == 'bar'
    assert ed.get_data(k8s_js)[0].double_nested.foo == 'foo'
    assert ed.get_data(k8s_js)[0].double_nested.foobar == 'foobar'
    assert ed.get_data(k8s_js)[0].double_nested.bar is None


def test_metadata_to_dict():
    md = fields.Metadata(['hello', 'foo', 'bar'])
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
    md = fields.Metadata(['annotations', 'foo', 'bar'])

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
                    'bar': 'YEAH',
                }
            }
        }
    }

    assert md.get_data(k8s_js) == 'YEAH'


def test_metadata_get_data_default():
    md = fields.Metadata(['annotations', 'default'], default='yeah')

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
