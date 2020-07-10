from pykorm import fields

def test_metadata_path():
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

    assert md.as_k8s_path('42') == wanted
