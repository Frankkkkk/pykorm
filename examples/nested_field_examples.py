import pykorm


class Score(pykorm.models.Nested):
    exterior: int = pykorm.fields.DataField('exterior')
    delicious: int = pykorm.fields.DataField('delicious', 10)


class ScoreMixin(object):
    score: Score = pykorm.fields.DictNestedField(Score, path=['spec', 'score'])


@pykorm.k8s_custom_object('pykorm.infomaniak.com', 'v1', 'apples')
class Apple(ScoreMixin, pykorm.ClusterModel):
    variety: str = pykorm.fields.Spec('variety', 'default-variety')


if __name__ == '__main__':
    ap = Apple(name='abc', score=Score(exterior=10))
    pk = pykorm.Pykorm()
    pk.save(ap)
    print(ap)
