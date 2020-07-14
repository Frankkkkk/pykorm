#!/usr/bin/env python3
# frank.villaro@infomaniak.com - DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE, etc.

import pykorm

@pykorm.k8s_custom_object('pykorm.infomaniak.com', 'v1', 'peaches')
class Peach(pykorm.NamespacedModel):
    variety: str = pykorm.fields.Spec('variety')

    def __init__(self, namespace: str, name:str, variety:str):
        self.namespace = namespace
        self.name = name
        self.variety = variety


pk = pykorm.Pykorm()
cake_peach = Peach(namespace='default', name='cake-peach', variety='Frost')
#pk.save(cake_peach)

for peach in Peach.query.all():
    print(str(peach))


for variety in ['frost', 'hot', 'cold']:
    for i in range(10):
        peach = Peach(namespace='default', name=f'{variety}-{i}', variety=variety)
#        pk.save(peach)

for p in Peach.query.filter_by(variety='hot'):
    print(f'MY FILTERED P is {p}')

# vim: set ts=4 sw=4 et:

