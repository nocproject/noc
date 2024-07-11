# NOC modules
from noc.inv.models.object import Object


class BaseTracer(object):
    @classmethod
    def is_applicable(cls, obj: Object) -> bool: ...
