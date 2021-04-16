# ----------------------------------------------------------------------
# RemoteSystem REST API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.main.models.remotesystem import RemoteSystem
from ..models.remotesystem import DefaultRemoteSystemItem, FormRemoteSystemItem
from ..utils.rest.document import DocumentResourceAPI


class RemoteSystemAPI(DocumentResourceAPI[RemoteSystem]):
    prefix = "/api/ui/remotesystem"
    model = RemoteSystem

    @classmethod
    def item_to_default(cls, item: RemoteSystem) -> DefaultRemoteSystemItem:
        return DefaultRemoteSystemItem(
            id=str(item.id),
            name=str(item.name),
            description=item.description,
            handler=item.handler,
            environment=item.environment,
            enable_admdiv=item.enable_admdiv,
            enable_administrativedomain=item.enable_administrativedomain,
            enable_authprofile=item.enable_authprofile,
            enable_container=item.enable_container,
            enable_link=item.enable_link,
            enable_managedobject=item.enable_managedobject,
            enable_managedobjectprofile=item.enable_managedobjectprofile,
            enable_networksegment=item.enable_networksegment,
            enable_networksegmentprofile=item.enable_networksegmentprofile,
            enable_object=item.enable_object,
            enable_service=item.enable_service,
            enable_serviceprofile=item.enable_serviceprofile,
            enable_subscriber=item.enable_subscriber,
            enable_subscriberprofile=item.enable_subscriberprofile,
            enable_resourcegroup=item.enable_resourcegroup,
            enable_ttsystem=item.enable_ttsystem,
            enable_project=item.enable_project,
            enable_label=item.enable_label,
            last_extract=item.last_extract,
            last_successful_extract=item.last_successful_extract,
            extract_error=item.extract_error,
            last_load=item.last_load,
            last_successful_load=item.last_successful_load,
            load_error=item.load_error,
        )

    @classmethod
    def item_to_form(cls, item: RemoteSystem) -> FormRemoteSystemItem:
        return FormRemoteSystemItem(
            name=str(item.name),
            description=item.description,
            handler=item.handler,
            environment=item.environment,
            enable_admdiv=item.enable_admdiv,
            enable_administrativedomain=item.enable_administrativedomain,
            enable_authprofile=item.enable_authprofile,
            enable_container=item.enable_container,
            enable_link=item.enable_link,
            enable_managedobject=item.enable_managedobject,
            enable_managedobjectprofile=item.enable_managedobjectprofile,
            enable_networksegment=item.enable_networksegment,
            enable_networksegmentprofile=item.enable_networksegmentprofile,
            enable_object=item.enable_object,
            enable_service=item.enable_service,
            enable_serviceprofile=item.enable_serviceprofile,
            enable_subscriber=item.enable_subscriber,
            enable_subscriberprofile=item.enable_subscriberprofile,
            enable_resourcegroup=item.enable_resourcegroup,
            enable_ttsystem=item.enable_ttsystem,
            enable_project=item.enable_project,
            enable_label=item.enable_label,
        )


router = RemoteSystemAPI().router
