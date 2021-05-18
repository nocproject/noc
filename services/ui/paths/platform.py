# ----------------------------------------------------------------------
# Platform REST API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from fastapi import APIRouter

# NOC modules
from noc.inv.models.platform import Platform
from noc.main.models.label import Label
from ..models.platform import (
    DefaultPlatformItem,
    FormPlatformItem,
)
from ..utils.ref import get_reference, get_reference_label
from ..utils.rest.document import DocumentResourceAPI
from ..utils.rest.op import FilterExact, FuncFilter, FilterIn

router = APIRouter()


class PlatformAPI(DocumentResourceAPI[Platform]):
    prefix = "/api/ui/platform"
    model = Platform
    list_ops = [
        FuncFilter("query", function=lambda qs, value: qs.filter(full_name__icontains=value[0])),
        FilterIn("id"),
        FilterExact("name"),
    ]
    sort_fields = ["full_name", "id"]

    @classmethod
    def item_to_default(cls, item: Platform) -> DefaultPlatformItem:
        return DefaultPlatformItem(
            id=str(item.id),
            name=str(item.name),
            description=item.description,
            full_name=str(item.full_name),
            vendor=get_reference(item.vendor),
            start_of_sale=item.start_of_sale,
            end_of_sale=item.end_of_sale,
            end_of_support=item.end_of_support,
            end_of_xsupport=item.end_of_xsupport,
            snmp_sysobjectid=item.snmp_sysobjectid,
            aliases=item.aliases,
            labels=[get_reference_label(ii) for ii in Label.objects.filter(name__in=item.labels)],
            effective_labels=[
                get_reference_label(ii)
                for ii in Label.objects.filter(name__in=item.effective_labels)
            ],
            uuid=str(item.uuid),
            bi_id=str(item.bi_id),
        )

    @classmethod
    def item_to_form(cls, item: Platform) -> FormPlatformItem:
        return FormPlatformItem(
            name=str(item.name),
            description=item.description,
            vendor=item.vendor,
            start_of_sale=item.start_of_sale,
            end_of_sale=item.end_of_sale,
            end_of_support=item.end_of_support,
            end_of_xsupport=item.end_of_xsupport,
            snmp_sysobjectid=item.snmp_sysobjectid,
            labels=item.labels,
        )


# Install endpoints
PlatformAPI(router)
