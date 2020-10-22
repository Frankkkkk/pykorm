#!/bin/bash

for f in tests/crds/*.yaml; do
	kubectl create -f $f
done

python -m pytest --kube-config=$KUBECONFIG


