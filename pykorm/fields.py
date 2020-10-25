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

    def to_dict(self, value) -> Dict:
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


class ListField(DataField):
    def __init__(self, nested_type, **kwargs):
        super().__init__(**kwargs)
        self.dict_nested_field = DictNestedField(nested_type=nested_type, path=[])

    def to_dict(self, multi_nested_value: list) -> Dict:
        result = []
        for nested_value in multi_nested_value:
            result.append(
                self.dict_nested_field.to_dict(nested_value)
            )
        return dpath.util.new({}, self.path, result)

    def get_data(self, k8s_dict: Dict):
        ret = []
        full_items = dpath.util.get(k8s_dict, self.fullpath) or []
        for sub_dict in full_items:
            ret.append(self.dict_nested_field.get_data(sub_dict))
        return ret


class DictNestedField(DataField):
    def __init__(self, nested_type, **kwargs):
        from pykorm.models import Nested

        if not issubclass(nested_type, Nested):
            raise Exception(f'Embedded type must be subclass of {Nested.__class__}, but found {nested_type.__class__}')
        self.nested_type = nested_type
        super().__init__(**kwargs)

    def to_dict(self, nested_value) -> Dict:
        result = {}
        if nested_value is None:
            nested_value = {}
            if self.allow_empty:  # allow empty for patch https://github.com/Frankkkkk/pykorm/issues/9#issuecomment-714217243
                return dpath.util.new(result, self.fullpath, None)
            return nested_value

        for attr, attr_type in self.nested_type._get_attributes().items():
            value = getattr(nested_value, attr)
            result = dpath.util.merge(result, attr_type.to_dict(value))
        if self.fullpath:
            return dpath.util.new({}, self.path, result)
        return result

    def get_data(self, k8s_dict: Dict):
        obj = self.nested_type()
        for attr, attr_type in self.nested_type._get_attributes().items():
            if self.fullpath:
                sub_dict = dpath.util.get(k8s_dict, self.fullpath, default=self.default)
            else:
                sub_dict = k8s_dict
            value = attr_type.get_data(sub_dict)
            setattr(obj, attr, value)
        return obj
