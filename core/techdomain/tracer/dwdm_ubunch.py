from inv.models.object import Object
from .base import BaseTracer


class DwdmUbunchTracer(BaseTracer):
    """
    Create channel between optical mux/demux
    """

    @classmethod
    def is_applicable(cls, obj: Object) -> bool:
        n = 0
        for c in obj.model.connections:
            if not c.protocols:
                continue
            for pvi in c.protocols:
                if pvi.protocol.code == "DWDM" and pvi.direction != ">" and pvi.discriminator:
                    n += 1
        return n > 1
