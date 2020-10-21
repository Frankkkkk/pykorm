import pykorm

conf = {
    "cluster1": {
        "host": "https://10.122.122.95:8443/k8s/clusters/c-xxxxx",
        "api_key": {
            "authorization": "Bearer k8stokenxxxxxxxx"
        },
        "verify_ssl": False
    }
}


@pykorm.pykorm.k8s_core(kind='Pod')
class Pod(pykorm.models.NamespacedModel):
    pass


pykorm.Pykorm.clusters_config = conf

if __name__ == '__main__':
    default_pods = Pod.query.filter_by(namespace='default').all()
    print(f'default pods: {default_pods}')
    cluster1_pods = Pod.query.using(cluster='cluster1').filter_by(namespace='default').all()
    print(f'cluster1 pods: {cluster1_pods}')
