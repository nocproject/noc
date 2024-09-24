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
    def setup(self, ep: Endpoint) -> JobRequest | None:
        """
        Gennerate Job request to setup endpoint.

        Args:
            ep: Endpoint to setup.

        Returns:
            JobRequest: with provisioning routines.
            None: No provisioning needed.
        """
        return None

    def cleanup(self, ep: Endpoint) -> JobRequest | None:
        """
        Generate Job request to cleanup endpoint.

        Args:
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

    @classmethod
    def get_controller_for_object(cls, obj: Object, name: str) -> "ProfileChannelController | None":
        """
        Get profile controller for object.

        Args:
            obj: Object instance.
            name: Controller's name.

        Returns:
            ProfileChannelController: if supported.
            None: if not supported.
        """
        mo = ProfileChannelController.get_managed_object(f"o:{obj.id}")
        # @todo: Move hardcode to model data
        profile = mo.profile.name if mo else "IRE-Polus.Horizon"
        # @todo: Consider custom
        mn = f"noc.sa.profiles.{profile}.controller.{name}"
        try:
            m = __import__(mn, {}, {}, "Controller")
            return m.Controller()
        except ImportError as e:
            self.logger.error("Cannot load profile controller: %s", e)
            return None
