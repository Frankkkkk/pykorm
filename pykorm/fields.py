from dataclasses import dataclass

class DataField:
    _root_dict_key: str = None
    path: str = None

    def __init__(self, path: str):
        self.path = path

    def as_k8s_path(self, value: str):
        leaf = value

        print(f'My path is {self.path}')

        path = self.path.strip('.')

        for dict_item in reversed(path.split('.')):
            leaf = {dict_item: leaf}

        return {self._root_dict_key: leaf}


    def get_data(self, k8s_dict):
        return k8s_dict[self._root_dict_key][self.path]


class Spec(DataField):
    _root_dict_key = 'spec'

class Metadata(DataField):
    _root_dict_key = 'metadata'
