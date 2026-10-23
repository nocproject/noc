# ----------------------------------------------------------------------
# Service REST API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from fastapi import APIRouter

# NOC modules
from noc.sa.models.service import Service
from noc.main.models.label import Label
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.service import ServiceProfile
from ..models.service import (
    DefaultServiceItem,
    FormServiceItem,
    PreviewServiceItem,
)
from ..utils.ref import get_reference, get_reference_label, get_reference_rg
from ..utils.rest.document import DocumentResourceAPI
from ..utils.rest.op import FilterExact, RefFilter

router = APIRouter()


class ServiceAPI(DocumentResourceAPI[Service]):
    prefix = "/api/ui/service"
    model = Service
    list_ops = [
        FilterExact("id"),
        RefFilter("profile", model=ServiceProfile),
        RefFilter("parent", model=Service),
        RefFilter("managed_object", model=ManagedObject),
    ]

    @classmethod
    def item_to_default(cls, item: Service) -> DefaultServiceItem:
        return DefaultServiceItem(
            id=str(item.id),
            profile=get_reference(item.profile),
            ts=item.ts,
            state=get_reference(item.state),
            state_changed=item.ts,
            parent=get_reference(item.parent),
            subscriber=get_reference(item.subscriber),
            supplier=get_reference(item.supplier),
            description=item.description,
            agreement_id=item.agreement_id,
            order_id=item.order_id,
            stage_id=item.stage_id,
            stage_name=item.stage_name,
            stage_start=item.stage_start,
            account_id=item.account_id,
            address=item.address,
            managed_object=get_reference(item.managed_object),
            nri_port=item.nri_port,
            labels=[get_reference_label(ii) for ii in Label.objects.filter(name__in=item.labels)],
            effective_labels=[
                get_reference_label(ii)
                for ii in Label.objects.filter(name__in=item.effective_labels)
            ],
            static_service_groups=[get_reference_rg(sg) for sg in item.static_service_groups],
            effective_service_groups=[get_reference_rg(sg) for sg in item.effective_service_groups],
            static_client_groups=[get_reference_rg(sg) for sg in item.static_client_groups],
            effective_client_groups=[get_reference_rg(sg) for sg in item.effective_client_groups],
            remote_system=get_reference(item.remote_system),
            remote_id=item.remote_id,
            bi_id=str(item.bi_id),
        )

    @classmethod
    def item_to_form(cls, item: Service) -> FormServiceItem:
        return FormServiceItem(
            profile=get_reference(item.profile),
            parent=get_reference(item.parent),
            subscriber=get_reference(item.subscriber),
            supplier=get_reference(item.supplier),
            description=item.description,
            agreement_id=item.agreement_id,
            order_id=item.order_id,
            stage_id=item.stage_id,
            stage_name=item.stage_name,
            stage_start=item.stage_start,
            account_id=item.account_id,
            address=item.address,
            managed_object=get_reference(item.managed_object),
            nri_port=item.nri_port,
            labels=item.labels,
            static_service_groups=item.static_service_groups,
            static_client_groups=item.static_client_groups,
        )

    @classmethod
    def item_to_preview(cls, item: Service) -> PreviewServiceItem:
        return PreviewServiceItem(
            id=str(item.id),
            profile=get_reference(item.profile),
            state=get_reference(item.state),
            parent=get_reference(item.parent),
            description=item.description or "",
            state_changed=item.state_changed,
            address=item.address or "",
        )


# Install router
ServiceAPI(router)
