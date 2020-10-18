import pykorm


@pykorm.pykorm.k8s_core(kind='Event')
class Event(pykorm.models.NamespacedModel):
    action: str = pykorm.fields.DataField('action')
    reason: str = pykorm.fields.DataField('reason')
    type: str = pykorm.fields.DataField('type')
    message: str = pykorm.fields.DataField('message')


@pykorm.pykorm.k8s_core(kind='Pod')
class Pod(pykorm.models.NamespacedModel):
    _conditions: list = pykorm.fields.Status('conditions')
    _containerStatuses: list = pykorm.fields.Status('containerStatuses', default=[])
    _containers: list = pykorm.fields.Spec('containers', default=[])
    _init_containers: list = pykorm.fields.Spec('initContainers', default=[])
    _initContainerStatuses: list = pykorm.fields.Spec('initContainerStatuses', default=[])
    phase: str = pykorm.fields.Status('phase')

    def get_events(self):
        return Event.query(overwrite_api_client=self._queryset.api_client).filter_by(
            namespace=self.namespace).filter_by_fields(**{'involvedObject.name': self.name}).all()

    @property
    def containers(self):
        containers_map = {}
        for container in self._containers:
            containers_map[container['name']] = {
                'name': container['name'],
                'initContainer': False,
                'ready': False
            }
        for container in self._init_containers:
            containers_map[container['name']] = {
                'name': container['name'],
                'initContainer': True,
                'ready': False
            }
        for container in self._initContainerStatuses + self._containerStatuses:
            if container['name'] in containers_map:
                containers_map[container['name']]['ready'] = container['ready']
        return list(containers_map.values())


if __name__ == '__main__':
    pods = Pod.query.filter_by(namespace='default').all()
    for pod in pods:
        print(f'pod {pod.name}, events: {pod.get_events()}')
