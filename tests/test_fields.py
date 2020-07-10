from pykorm import fields

def test_metadata_to_dict():
    md = fields.Metadata('hello.foo.bar')
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
    md = fields.Metadata('.annotations.foo.bar')

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
