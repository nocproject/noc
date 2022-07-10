# ---------------------------------------------------------------------
# VCDomain model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from builtins import range, object
from django.db import models

# NOC modules
from noc.core.model.base import NOCModel
from noc.main.models.style import Style
from noc.main.models.label import Label
from noc.core.model.decorator import on_delete_check
from .vctype import VCType
from .vcfilter import VCFilter


@Label.match_labels("vcdomain", allowed_op={"="})
@on_delete_check(
    check=[
        ("inv.Interface", "vc_domain"),
        ("sa.ManagedObject", "vc_domain"),
        ("vc.VC", "vc_domain"),
        ("vc.VCBindFilter", "vc_domain"),
        ("vc.VCDomainProvisioningConfig", "vc_domain"),
    ],
    ignore=[("inv.MACDB", "vc_domain")],
    clean_lazy_labels="vcdomain",
)
class VCDomain(NOCModel):
    """
    Virtual circuit domain, allows to separate unique VC spaces
    """

    class Meta(object):
        verbose_name = "VC Domain"
        verbose_name_plural = "VC Domains"
        db_table = "vc_vcdomain"
        app_label = "vc"

    name = models.CharField("Name", max_length=64, unique=True)
    description = models.TextField("Description", blank=True, null=True)
    type = models.ForeignKey(VCType, verbose_name="Type", on_delete=models.CASCADE)
    enable_provisioning = models.BooleanField("Enable Provisioning", default=False)
    enable_vc_bind_filter = models.BooleanField("Enable VC Bind filter", default=False)
    style = models.ForeignKey(
        Style, verbose_name="Style", blank=True, null=True, on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name

    @classmethod
    def get_for_object(cls, managed_object):
        """
        Find VC Domain for Managed Object
        :param managed_object: Managed Object instance
        :return: VC Domain instance or None
        """
        return managed_object.vc_domain

    def get_free_label(self, vc_filter=None):
        """
        Find free label in VC Domain
        :param vc_filter: Optional VC Filter to restrict labels
        :type vc_filter: VCFilter
        :returns: Free label or None
        :rtype: int or None
        """
        from .vc import VC

        l_min = self.type.label1_min
        l_max = self.type.label1_max
        # Get valid ranges
        if vc_filter is None:
            chunks = [(l_min, l_max)]  # No filter
        else:
            chunks = VCFilter.compile(vc_filter.expression)
        # Find first free
        for x, y in chunks:
            if x > y or y < l_min or x > l_max:
                continue  # Skip chunk outside of type's range
            for ll in range(max(l_min, x), min(l_max, y) + 1):
                if not VC.objects.filter(vc_domain=self, l1=ll).exists():
                    return ll  # Return first free found
        return None  # Nothing found

    @classmethod
    def get_default(cls):
        return VCDomain.objects.get(name="default")

    @classmethod
    def iter_lazy_labels(cls, vcdomain: "VCDomain"):
        yield f"noc::vcdomain::{vcdomain.name}::="
