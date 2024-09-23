# ----------------------------------------------------------------------
# ProfileChannelController
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.runner.models.jobreq import JobRequest
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.channel import Channel
from noc.inv.models.endpoint import Endpoint
from noc.inv.models.object import Object
from .base import BaseProfileController


class ProfileChannelController(BaseProfileController):
    def setup(self, channel: Channel, ep: Endpoint) -> JobRequest | None:
        """
        Gennerate Job request to setup endpoint.

        Args:
            channel: Channel instance.
            ep: Endpoint to setup.

        Returns:
            JobRequest: with provisioning routines.
            None: No provisioning needed.
        """
        return None

    def cleanup(self, channel: Channel, ep: Endpoint) -> JobRequest | None:
        """
        Generate Job request to cleanup endpoint.

        Args:
            channel: Channel instance.
            ep: Endpoint to setup.

        Returns:
            JobRequest: with provisioning routines.
            None: No provisioning needed.
        """
        return None

    @classmethod
    def get_object(cls, resource: str) -> Object | None:
        """
        Get object for resource.

        Args:
            resource: Resource reference.

        Returns:
            Object: in case of success.
            None: if object cannot be resolved.

        Raises:
            ValueError: On invalid scheme.
        """
        parts = resource.split(":")
        if parts[0] == "o":
            return Object.get_by_id(parts[1])
        msg = f"invalid scheme: {parts[0]}"
        raise ValueError(msg)

    @classmethod
    def get_managed_object(cls, resource: str) -> ManagedObject | None:
        """
        Get managed object for resource.

        Args:
            resource: Resource reference.

        Returns:
            ManagedObject: If found.
            None: Otherwise.

        Raises:
            ValueError: On unknows resource schema.
        """
        parts = resource.split(":")
        match parts[0]:
            case "o":
                obj = cls.get_object(resource)
                while obj:
                    mo_id = obj.get_data("management", "managed_object")
                    if mo_id:
                        return ManagedObject.get_by_id(mo_id)
                    obj = obj.parent
                return None
            case _:
                msg = f"unknown schema: {parts[0]}"
                raise ValueError(msg)
