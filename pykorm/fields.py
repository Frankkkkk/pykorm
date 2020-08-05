from typing import Dict


class DataField:
    _root_dict_key: str
    _split_dots = True
    path: str
    default: object
    readonly: bool = False

    def __init__(self, path: str, default=None, readonly: bool = False):
        self.path = path.strip('.')
        self.default = default
        self.readonly = readonly

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        return f'<pykorm/{cls_name}: {self.path}>'


    def to_dict(self, value: str) -> Dict:
        path = self.path

        leaf = value
        if self._split_dots:
            for dict_item in reversed(path.split('.')):
                leaf = {dict_item: leaf}
        else:
            leaf = {path: value}

        for dict_item in reversed(self._root_dict_key.split('.')):
            leaf = {dict_item: leaf}

        return leaf


    def get_data(self, k8s_dict: Dict):
        for elem in self._root_dict_key.split('.'):
            k8s_dict = k8s_dict.get(elem, {})

        if self._split_dots:
            for elem in self.path.split('.'):
                if elem in k8s_dict:
                    k8s_dict = k8s_dict[elem]
                else:
                    return self.default
        else:
            k8s_dict = k8s_dict.get(self.path, self.default)

        return k8s_dict


class Spec(DataField):
    _root_dict_key = 'spec'


class Metadata(DataField):
    _root_dict_key = 'metadata'


class MetadataAnnotation(DataField):
    _root_dict_key = 'metadata.annotations'
    _split_dots = False


class Status(DataField):
    _root_dict_key = 'status'

