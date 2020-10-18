#!/usr/bin/env python3
# frank.villaro@infomaniak.com - DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE, etc.

import pykorm


class Score(pykorm.models.NestedField):
    exterior: int = pykorm.fields.DataField('exterior')
    delicious: int = pykorm.fields.DataField('delicious', 10)


class ScoreMixin(object):
    score: Score = pykorm.fields.DictNestedField(Score, path='spec@score')


@pykorm.k8s_custom_object('pykorm.infomaniak.com', 'v1', 'peaches')
class Peach(ScoreMixin, pykorm.NamespacedModel):
    variety: str = pykorm.fields.Spec('variety')


pk = pykorm.Pykorm()
cake_peach = Peach(namespace='default', name='cake-peach', variety='Frost')
# pk.save(cake_peach)

for peach in Peach.query.all():
    print(str(peach))

for variety in ['frost', 'hot', 'cold']:
    for i in range(10):
        peach = Peach(namespace='default', name=f'{variety}-{i}', variety=variety, score={
            'exterior': i,
            'delicious': i
        })
        pk.apply(peach)

for p in Peach.query.filter_by(variety='hot').all():
    print(f'MY FILTERED P is {p}')

# vim: set ts=4 sw=4 et:
