from dataclasses import dataclass

class DataField:
    pass

@dataclass
class Spec(DataField):
    path: str

    def get_data(self, k8s_dict):
        return k8s_dict['spec'][self.path]
