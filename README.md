# pykorm - Python Kubernetes Object-relational mapping (ORM)

`pykorm` is a simple library that links your models to their `kubernetes` counterpart.

Each model and instance on your code is thus directly linked to your kubernetes
cluster and modifications are thus reflected both ways.

# Examples
## Namespaced Custom Resource
### Setup
First of all, you need to have Custom Resource Definitions on your cluster.  
This README will use the following Namespaced resource. You can apply it on your 
cluster with `kubectl`.

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: peaches.pykorm.infomaniak.com
spec:
  group: pykorm.infomaniak.com
  names:
    kind: Peach
    listKind: PeachList
    plural: peaches
    singular: peach
  scope: Namespaced
  versions:
  - name: v1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              variety:
                type: string
            required:
              - variety


    additionalPrinterColumns:
    - name: Variety
      type: string
      description: The variety of the peach
      jsonPath: .spec.variety
```

### Class definition
In order to link a python class to a kubernetes CustomResourceDefinition,
you need to inherit the class from pykorm's `NamespacedModel` or `ClusterModel` 
and annotate it with the kubernetes CRD information like so:
```python
import pykorm

@pykorm.k8s_custom_object('pykorm.infomaniak.com', 'v1', 'peaches')
class Peach(pykorm.NamespacedModel):
    variety: str = pykorm.fields.Spec('variety')

    def __init__(self, namespace: str, name:str, variety:str):
        self.namespace = namespace
        self.name = name
        self.variety = variety
```

Notice that a class inheriting from `pykorm.NamespacedModel` already has the 
`name` and `namespace` fields setup.

### Create a CR
In order to create a kubernetes custom resource from python, you just
have to instantiate the class and save it with `Pykorm.save()`:
```python
import pykorm
pk = pykorm.Pykorm()

cake_peach = Peach(namespace='default', name='cake-peach', variety='Frost')
pk.save(cake_peach)
```
as you can see, the model is instantly ensured in kubernetes:
```bash
$ kubectl get peach -n default
NAME         VARIETY
cake-peach   Frost
```

### List resources
Pykorm can also list resources from kubernetes
```python
>>> all_peaches = Peach.query.all()
>>> for peach in all_peaches:
>>>  print(peach)
<Peach namespace=default, name=cake-peach, variety=Frost>
```

You can even filter resources by some criterion:
```python
>>> Peach.query.filter_by(name='cake-peach')
[<Peach namespace=default, name=cake-peach, variety=Frost>]
>>> Peach.query.filter_by(namespace='kube-system')
[]
```

### Delete resources
You can delete a resource with `pykorm` too:
```python
pk.delete(peach)
```
```bash
$ kubectl get peach
No resources found in default namespace.
```

## More examples
For more examples, don't hesitate to look into the `examples/` directory


# Is pykorm stable ?
pykorm is still very young and very naive. It's also missing quite a lot of 
features (relationships, etc.).
It was originally created because a lot of boilerplate code was written each
time a kubernetes custom object had to be interfaced with python 
code.

Work on `pykorm` is actually on the way. Don't hesitate to contribute to the 
project if you have the energy for it !

## Limitations
As of now, pykorm only supports CustomResourceDefinitions (as accessed by the `kubernetes.client.CustomObjectsApi` API)
and doesn't yet work with "native" resources like `Node`, `Deployment`, `Service`, etc.


## Equivalences
| Python   | Kubernetes  |
|----------|-------------|
| Class    | CustomResourceDefinition |
| Instance | CustomResource |
