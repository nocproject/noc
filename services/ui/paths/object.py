# ----------------------------------------------------------------------
# Object REST API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from fastapi import APIRouter

# NOC modules
from noc.inv.models.object import Object
from noc.inv.models.objectmodel import ObjectModel
from noc.main.models.label import Label
from ..models.object import DefaultObjectItem, FormObjectItem, PointItem
from ..utils.ref import get_reference, get_reference_label
from ..utils.rest.document import DocumentResourceAPI
from ..utils.rest.op import RefFilter, FuncFilter

router = APIRouter()


class ObjectAPI(DocumentResourceAPI[Object]):
    prefix = "/api/ui/object"
    model = Object
    list_ops = [
        FuncFilter("query", function=lambda qs, value: qs.filter(name__regex=value)),
        RefFilter("container", model=Object),
        RefFilter("model", model=ObjectModel),
    ]

    @classmethod
    def item_to_default(cls, item: Object) -> DefaultObjectItem:
        point = None
        if item.point:
            x, y = item.point["coordinates"]
            point = PointItem(x=x, y=y)
        return DefaultObjectItem(
            id=str(item.id),
            name=str(item.name),
            model=get_reference(item.model),
            layer=get_reference(item.layer),
            point=point,
            container=get_reference(item.container),
            remote_system=get_reference(item.remote_system),
            remote_id=item.remote_id,
            bi_id=str(item.bi_id),
            labels=[get_reference_label(ll) for ll in Label.objects.filter(name__in=item.labels)],
            effective_labels=[
                get_reference_label(ll)
                for ll in Label.objects.filter(name__in=item.effective_labels)
            ],
        )

    @classmethod
    def item_to_form(cls, item: Object) -> FormObjectItem:
        return FormObjectItem(
            name=item.name,
            model=item.model,
            labels=item.labels,
        )


# Install endpoints
ObjectAPI(router)
