import pykorm


@pykorm.pykorm.k8s_core(kind='Pod')
class Pod(pykorm.models.NamespacedModel):
    pass


if __name__ == '__main__':
    pods = Pod.query.filter_by(namespace='default').filter_by_labels(app='helloworld').all()
    print(pods)

    # [<Pod created_at=2020-10-14T09:29:30Z name=helloworld-749fcb9cbb-pczst namespace=default>]
