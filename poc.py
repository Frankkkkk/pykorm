#!/usr/bin/env python3
# frank.villaro@infomaniak.com - DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE, etc.

import kubernetes
import logging
import http.client

logging.basicConfig(level=logging.DEBUG)


def load_kube_config():
    kubernetes.config.load_kube_config()


load_kube_config()

cust_api = kubernetes.client.CustomObjectsApi()
n1 = cust_api.get_cluster_custom_object('', 'v1', 'nodes', 'piktest-c25v-0')
print(n1)



# vim: set ts=4 sw=4 et:

