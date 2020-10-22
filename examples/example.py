#!/usr/bin/env python3
# frank.villaro@infomaniak.com - DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE, etc.

import pykorm


@pykorm.k8s_custom_object('pykorm.infomaniak.com', 'v1', 'peaches')
class Peach(pykorm.NamespacedModel):
    variety: str = pykorm.fields.Spec('variety')


pk = pykorm.Pykorm()
cake_peach = Peach(namespace='default', name='cake-peach', variety='Frost')
# pk.save(cake_peach)

for variety in ['frost', 'hot', 'cold']:
    for i in range(0):
        peach = Peach(namespace='default', name=f'{variety}-{i}', variety=variety)
        pk.apply(peach)

print(list(Peach.query.all()))

print('My hot peaches are:')
for p in Peach.query.filter_by(variety='hot').all():
    print(p)

print('The cold peaches are:')
for p in Peach.query.filter_by(variety='cold').all():
    print(p)

# vim: set ts=4 sw=4 et:
