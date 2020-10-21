from conftest import Peach


def test_filter_attr(pk, kube):
    all_peaches = {}
    for variety in ['a', 'b', 'c']:
        peaches = []
        for num in range(1):
            p = Peach(namespace=kube.namespace, name=f'{variety}-{num}', variety=variety)
            peaches.append(p)
            pk.save(p)
        all_peaches[variety] = peaches



    # Do a query
    a_peaches = Peach.query.filter_by(variety='a').all()
    assert(set(a_peaches) == set(all_peaches['a']))


    # Do a second query that is disjoint with the first one
    b_peaches = Peach.query.filter_by(variety='b').all()
    assert(b_peaches == all_peaches['b'])


def test_filter_chain(pk, kube):
    all_peaches = {}
    for variety in ['a', 'b', 'c']:
        pp = {}
        for price in [1, 2, 3]:
            peaches = []
            for num in range(1):
                p = Peach(namespace=kube.namespace, name=f'{variety}-{price}-{num}', variety=variety, price=price)
                peaches.append(p)
                pk.save(p)
            pp[price] = peaches
        all_peaches[variety] = pp

    # Do a chain query
    a_1_peaches = Peach.query.filter_by(namespace=kube.namespace).filter_by(variety='a').filter_by(price=1).all()
    assert set(a_1_peaches) == set(all_peaches['a'][1])

    # Search on a NS where they're nowhere to be found
    no_peaches = Peach.query.filter_by(namespace='idontexist').filter_by(variety='a').filter_by(price=1).all()
    assert no_peaches == []

    # Search for an unknown variety
    rarepeaches = Peach.query.filter_by(namespace=kube.namespace).filter_by(variety='rare').filter_by(price=1).all()
    assert rarepeaches == []

