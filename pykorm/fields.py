from typing import Dict

import dpath.util


class DataField:
    _root_dict_key = ''
    _split_dots = True
    path: str
    default: object
    editable: bool = True
    readonly: bool = False
    required: bool = False
    choices: tuple = None
    allow_empty: bool = False
    _include_slices = True

    def __init__(self, path: str, default=None, editable: bool = True, required: bool = False, choices: tuple = None,
                 readonly: bool = False, allow_empty: bool = False):
        self.path = path.strip('.')
        self.default = default
        self.editable = editable
        self.required = required
        self.choices = choices
        self.readonly = readonly
        self.allow_empty = allow_empty

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        return f'<pykorm/{cls_name}: {self.path}>'

    @property
    def fullpath(self):
        paths = []
        if self._root_dict_key:
            paths.append(self._root_dict_key)
        paths.append(self.path)
        return '@'.join(paths)

    @staticmethod
    def preprocessor(x):
        return x

    @staticmethod
    def postprocessor(x):
        return x

    def to_dict(self, value: str) -> Dict:
        result = {}
        path = self.fullpath
        if value is None and self.default is not None:
            value = self.default
        if value is None and (not self.allow_empty):
            return {}
        if value is not None:
            value = self.preprocessor(value)
        return dpath.util.new(result, path, value, separator='@')

    def get_data(self, k8s_dict: Dict):
        path = self.fullpath
        data = dpath.util.get(k8s_dict, path, separator='@', default=self.default)
        return self.postprocessor(data) if data is not None else data


class Spec(DataField):
    _root_dict_key = 'spec'


class Metadata(DataField):
    _root_dict_key = 'metadata'


class MetadataAnnotation(DataField):
    _root_dict_key = 'metadata@annotations'
    _split_dots = False


class Status(DataField):
    _root_dict_key = 'status'


class BaseNestedField(DataField):
    nested = None

    def __init__(self, nested, *args, **kwargs):
        self.nested = nested
        self.nested._root_dict_key = kwargs['path']
        super().__init__(*args, **kwargs)


class ListNestedField(BaseNestedField, list):
    def to_dict(self, value):
        result = {}
        path = self.fullpath
        rets = []
        for item in value or []:
            data = {}
            for attr_name, attr_type in self.nested._get_attributes().items():
                v = getattr(item, attr_name)
                v = attr_type.to_dict(v)
                dpath.util.merge(data, v)
            rets.append(data)
        return dpath.util.new(result, path, rets, separator='@')

    def get_data(self, k8s_dict: Dict):
        ret = []
        path = self.fullpath
        items = dpath.util.get(k8s_dict, path, separator='@', default=self.default) or []
        for item in items:
            item_obj = self.nested()
            for field, field_type in item_obj._get_attributes().items():
                if isinstance(field_type, BaseNestedField):
                    data = field_type.get_data(item)
                else:
                    path = field_type.path
                    data = dpath.util.get(item, path, separator='@', default=field_type.default)
                    # data = dpath.util.get(item, path, separator='@')
                setattr(item_obj, field, field_type.postprocessor(data))
            ret.append(item_obj)
        return ret


class DictNestedField(BaseNestedField):
    def to_dict(self, item):
        ret = {}
        if item is None:
            if self.allow_empty:
                return dpath.util.new(ret, self.fullpath, None, separator='@')
            return {}
            # return dpath.util.new(ret, self.path, self.default, separator='@')
        for attr_name, attr_type in self.nested._get_attributes().items():
            paths = []
            if self.path:
                paths.append(self.path)
            # if attr_type._root_dict_key:
            #     paths.append(attr_type._root_dict_key)
            value = getattr(item, attr_name)
            if value is not None:
                value = attr_type.to_dict(value)
                value = dpath.util.get(value, attr_type.fullpath, separator='@', default=attr_type.default)
            else:
                value = attr_type.default
                if value is None:
                    continue
            if isinstance(self, DictNestedField):
                paths.append(attr_type.fullpath)
            path = '@'.join(paths)
            ret = dpath.util.new(ret, path, value, separator='@')
        return ret

    def get_data(self, k8s_dict: Dict):
        ret = self.nested()
        parent_value = dpath.util.get(k8s_dict, self.path, separator='@', default=None)
        if parent_value is None:
            return None
        for attr_name, attr_type in self.nested._get_attributes().items():
            paths = [self.path, attr_type.fullpath]
            path = '@'.join(paths)
            if isinstance(attr_type, BaseNestedField):
                new_dict = {}
                new_value = dpath.util.get(k8s_dict, path, separator='@', default=None)
                if new_value is None:
                    continue
                new_dict = dpath.util.new(new_dict, attr_type.fullpath,
                                          new_value,
                                          separator='@')
                value = attr_type.get_data(new_dict)
            else:
                value = dpath.util.get(k8s_dict, path, separator='@', default=None)
            if value is None:
                continue
            value = attr_type.postprocessor(value)
            setattr(ret, attr_name, value)
        return ret
