

class BaseQuery:
    baseobject: type = None

    def __init__(self, baseobject: type):
        self.baseobject = baseobject

    def all(self):
        print(f"Yeahman. My uid is plural is {self.baseobject._pykorm_group}")



class NamespacedObjectQuery(BaseQuery):
    pass


class ClusterObjectQuery(BaseQuery):
    pass


class PykormModel:
    name = None
    _k8s_uid = None
    query: BaseQuery = None


class NamespacedModel(PykormModel):
    _pykorm_group: str = None
    _pykorm_version: str = None
    _pykorm_plural: str = None


class ClusterModel(PykormModel):
    pass


def _process_cls(cls, query_class, group: str, version: str, plural: str):
    cls._pykorm_group = group
    cls._pykorm_version = version
    cls._pykorm_plural = plural
    cls.query = query_class(baseobject=cls)
    return cls


def k8s_custom_object(group: str, version: str, plural: str):
    def wrap(cls):
        if issubclass(cls, ClusterModel):
            query_class = ClusterObjectQuery
        elif issubclass(cls, NamespacedModel):
            query_class = NamespacedObjectQuery
        else:
            raise Exception(f"Class {cls} doesn't seem to inherit from either ClusterModel nor NamespacedModel")

        return _process_cls(cls, query_class, group, version, plural)

    return wrap


@k8s_custom_object(group='group', version='version', plural='plural')
class MyDB(NamespacedModel):
    def quack(self):
        print('Quack !')



mdb = MyDB()
mdb.quack()
#mdb.query.all()
#print(mdb._pykorm_group)

MyDB.query.all()

