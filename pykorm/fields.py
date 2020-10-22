from typing import Dict

import dpath.util


class DataField:
    _root_dict_key = []
    path: str
    default: object
    readonly: bool = False
    required: bool = False
    allow_empty: bool = False

    def __init__(self, path: str, default=None, required: bool = False,
                 readonly: bool = False, allow_empty: bool = False):
        if type(path) == str:
            self.path = [path]
        elif type(path) == list:
            self.path = path
        else:
            raise Exception('param path must be a string or list')

        self.default = default
        self.required = required
        self.readonly = readonly
        self.allow_empty = allow_empty

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        return f'<pykorm/{cls_name}: {self.path}>'

    @property
    def fullpath(self):
        return self._root_dict_key + self.path

    @staticmethod
    def preprocessor(x):
        return x

    @staticmethod
    def postprocessor(x):
        return x

    def to_dict(self, value: str) -> Dict:
        result = {}
        if value is None and self.default is not None:
            value = self.default
        if value is None and (not self.allow_empty):
            return {}
        if value is not None:
            value = self.preprocessor(value)

        return dpath.util.new(result, self.fullpath, value)

    def get_data(self, k8s_dict: Dict):
        data = dpath.util.get(k8s_dict, self.fullpath, default=self.default)
        return self.postprocessor(data) if data is not None else data


class Spec(DataField):
    _root_dict_key = ['spec']


class Metadata(DataField):
    _root_dict_key = ['metadata']


class MetadataAnnotation(DataField):
    _root_dict_key = ['metadata', 'annotations']


class Status(DataField):
    _root_dict_key = ['status']
