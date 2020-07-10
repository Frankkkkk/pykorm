from dataclasses import dataclass
from typing import Dict

class DataField:
    _root_dict_key: str = None
    path: str = None

    def __init__(self, path: str):
        self.path = path.strip('.')

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        return f'<pykorm/{cls_name}: {self.path}>'

    def to_dict(self, value: str) -> Dict:
        leaf = value

        path = self.path

        for dict_item in reversed(path.split('.')):
            leaf = {dict_item: leaf}

        return {self._root_dict_key: leaf}


    def get_data(self, k8s_dict: Dict) -> str:
        full_path = self._root_dict_key + '.' + self.path
        print(f'My full path is {full_path}')
        print(k8s_dict)

        for elem in full_path.split('.'):
            k8s_dict = k8s_dict[elem]
            print(f'Got {elem} -> {k8s_dict}')
        return k8s_dict


class Spec(DataField):
    _root_dict_key = 'spec'

class Metadata(DataField):
    _root_dict_key = 'metadata'
