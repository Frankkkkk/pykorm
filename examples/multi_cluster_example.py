import kubernetes
import pykorm


@pykorm.pykorm.k8s_core(kind='Namespace')
class Namespace(pykorm.models.ClusterModel):
    pass



cluster_cl1 = kubernetes.client.Configuration()
cluster_cl2 = kubernetes.client.Configuration()

kubernetes.config.load_kube_config('/home/alice/kubeconfig-cl1', client_configuration=cluster_cl1)
kubernetes.config.load_kube_config('/home/bob/kubeconfig-cl2', client_configuration=cluster_cl2)

clusters = {
    "cluster-cl1": cluster_cl1,
    "cluster-cl2": cluster_cl2,
    "cluster-cl3": {
        "host": "https://10.122.122.95:8443/k8s/clusters/c-xxxxx",
        "api_key": {
            "authorization": "Bearer k8stokenxxxxxxxx"
        },
        "verify_ssl": False
    },
}

pykorm.Pykorm.clusters_config = clusters
pk = pykorm.Pykorm()


# Create a NS on cluster 1
ns_on_cl1 = Namespace(name='ns-on-cluster-cl1')
pk.save(ns_on_cl1, cluster='cluster-cl1')

# Show ns on cl1 and cl2
ns_cl1 = Namespace.query.using(cluster='cluster-cl1').all()
ns_cl2 = Namespace.query.using(cluster='cluster-cl2').all()

print(f"Here are the ns on cl1 and cl2:\n{ns_cl1}\n{ns_cl2}")

print("Will save ns 'ns-on-cluster-cl1' on cl2")
ns1 = list(filter(lambda x: x.name == 'ns-on-cluster-cl1', ns_cl1))[0]

# Sadly, to save a resource on another cluster you need to remove
# the uid field
Namespace._k8s_uid.readonly = False  # Make it read/write
ns1._k8s_uid = None
# And save it on cluster cl2
pk.save(ns1, cluster='cluster-cl2')

print("And here are now the ns of cl2")
print(Namespace.query.using(cluster='cluster-cl2').all())
