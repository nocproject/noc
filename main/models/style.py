# ---------------------------------------------------------------------
# Style model model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from threading import Lock
from typing import Optional, Dict, Any
import operator

# Third-party modules
from django.db import models
import cachetools

# NOC models
from noc.core.model.base import NOCModel
from noc.core.model.decorator import on_delete_check

id_lock = Lock()


@on_delete_check(
    check=[
        ("inv.InterfaceProfile", "style"),
        ("sa.ManagedObjectProfile", "style"),
        ("crm.SubscriberProfile", "style"),
        ("crm.SupplierProfile", "style"),
        ("sla.SLAProfile", "style"),
        ("inv.CPEProfile", "style"),
        ("inv.NetworkSegmentProfile", "style"),
        ("inv.SensorProfile", "style"),
        ("ip.AddressProfile", "style"),
        ("ip.PrefixProfile", "style"),
        ("vc.VPNProfile", "style"),
        ("fm.AlarmSeverity", "style"),
        ("peer.ASProfile", "style"),
        ("phone.PhoneNumberProfile", "style"),
        ("phone.PhoneRangeProfile", "style"),
        ("fm.ActiveAlarm", "custom_style"),
        ("vc.VLANProfile", "style"),
        ("vc.L2DomainProfile", "style"),
    ]
)
class Style(NOCModel):
    """
    CSS Style
    """

    class Meta(object):
        verbose_name = "Style"
        verbose_name_plural = "Styles"
        ordering = ["name"]
        app_label = "main"
        db_table = "main_style"

    name = models.CharField("Name", max_length=64, unique=True)
    font_color = models.IntegerField("Font Color", default=0)
    background_color = models.IntegerField("Background Color", default=0xFFFFFF)
    bold = models.BooleanField("Bold", default=False)
    italic = models.BooleanField("Italic", default=False)
    underlined = models.BooleanField("Underlined", default=False)
    is_active = models.BooleanField("Is Active", default=True)
    description = models.TextField("Description", null=True, blank=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: int) -> Optional["Style"]:
        return Style.objects.filter(id=oid).first()

    @property
    def style(self) -> Dict[str, str]:
        """
        CSS Style
        """
        r = {
            "color": f"#{self.font_color:06X}",
            "background-color": f"#{self.background_color:06X}",
        }
        if self.bold:
            r["font-weight"] = "bold"
        if self.italic:
            r["font-style"] = "italic"
        if self.underlined:
            r["text-decoration"] = "underline"
        return r

    @property
    def css_class(self) -> Optional[str]:
        return f"noc-color-{self.id}"

    def get_css_class(self) -> Optional[str]:
        return self.css_class

    @classmethod
    def get_scheme(cls) -> Dict[str, Any]:
        """
        Get schema snapshot.
        """

        def q(s: Style) -> Dict[str, Any]:
            r = {"name": s.css_class}
            r.update(s.style)
            return r

        return {"style": [q(x) for x in Style.objects.filter(is_active=True)]}
