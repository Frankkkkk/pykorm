from typing import Dict


class DataField:
    _root_dict_key: str
    path: str
    readonly: bool = False

    def __init__(self, path: str, readonly: bool = False):
        self.path = path.strip('.')
        self.readonly = readonly

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        return f'<pykorm/{cls_name}: {self.path}>'

    def to_dict(self, value: str) -> Dict:
        path = self.path

        leaf = value
        for dict_item in reversed(path.split('.')):
            leaf = {dict_item: leaf}

        return {self._root_dict_key: leaf}


    def get_data(self, k8s_dict: Dict):
        full_path = self._root_dict_key + '.' + self.path

        for elem in full_path.split('.'):
            k8s_dict = k8s_dict[elem]
        return k8s_dict


class Spec(DataField):
    _root_dict_key = 'spec'


class Metadata(DataField):
    _root_dict_key = 'metadata'

