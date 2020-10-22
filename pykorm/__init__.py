import dpath

from .fields import Spec, Metadata, MetadataAnnotation  # noqa
from .models import NamespacedModel, ClusterModel  # noqa
from .pykorm import k8s_custom_object, k8s_core, Pykorm  # noqa

dpath.options.ALLOW_EMPTY_STRING_KEYS = True
