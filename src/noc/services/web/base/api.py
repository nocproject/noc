# ---------------------------------------------------------------------
# API decorators
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections.abc import Callable
from typing import TypeVar, Any, Concatenate, ParamSpec

# Third-party modules
from django.http import HttpRequest

# NOC modules
from noc.sa.interfaces.base import DictParameter
from .access import HasPerm, Permit, Deny, Permission

__all__ = ["api", "view"]

P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("T")
Self = TypeVar("Self")


def view(
    url: str,
    access: str | bool | Permission,
    url_name: str | None = None,
    menu: list[str] | None = None,  # @todo: dead code?
    method: list[str] | None = None,
    validate: dict[str, Any] | None = None,
    api: bool = False,
) -> Callable[
    [Callable[Concatenate[Self, HttpRequest, P], R]], Callable[Concatenate[Self, HttpRequest, P], R]
]:
    """
    Register a method as an application view.

    The decorator attaches routing, access control, request validation,
    and other view metadata to the decorated method. The collected metadata
    is later used by the application to build URL mappings and process
    incoming requests.

    Args:
        url: URL path relative to the application root.
        access: Access policy. May be a permission name, a boolean allowing
            or denying access, or a custom permission object.
        url_name: Optional URL name for reverse URL resolution.
        menu: Optional menu path associated with the view.
        method: Allowed HTTP methods. If omitted, all methods are accepted.
        validate: Optional request validation schema.
        api: Whether the view is exposed as an API endpoint.

    Returns:
        A decorator that configures the decorated view method.
    """

    def decorate(
        f: Callable[Concatenate[Self, HttpRequest, P], R],
    ) -> Callable[Concatenate[Self, HttpRequest, P], R]:
        f.url = url
        f.url_name = url_name
        # Process access
        if isinstance(access, bool):
            f.access = Permit() if access else Deny()
        elif isinstance(access, str):
            f.access = HasPerm(access)
        else:
            f.access = access
        f.menu = menu
        f.method = method
        f.api = api
        if isinstance(validate, dict):
            f.validate = DictParameter(attrs=validate)
        else:
            f.validate = validate
        return f

    return decorate


class ViewAPI:
    """
    API view decorator factory.

    Provides HTTP method-specific decorators that create API endpoints
    using the common :func:`view` decorator.

    Example:
        @api.get("^brief_lookup/$",
            access="lookup",
        )
        def api_brief(self, request: HttpRequest):
            ...
    """

    def get(
        self,
        url: str,
        /,
        *,
        access: str | bool | Permission,
        url_name: str | None = None,
        menu: list[str] | None = None,  # @todo: dead code?
        validate: dict[str, Any] | None = None,
    ):
        """
        Decorate a GET API endpoint.

        Args:
            url: URL pattern relative to the application root.
            access: Access control rule.
            url_name: Optional URL name.
            menu: Optional menu entry metadata.
            validate: Optional request parameter validation schema.

        Returns:
            A view decorator.
        """
        return view(
            url=url,
            method=["GET"],
            access=access,
            url_name=url_name,
            menu=menu,
            validate=validate,
            api=True,
        )

    def post(
        self,
        url: str,
        /,
        *,
        access: str | bool | Permission,
        url_name: str | None = None,
        menu: list[str] | None = None,  # @todo: dead code?
        validate: dict[str, Any] | None = None,
    ):
        """
        Decorate a POST API endpoint.

        Args:
            url: URL pattern relative to the application root.
            access: Access control rule.
            url_name: Optional URL name.
            menu: Optional menu entry metadata.
            validate: Optional request parameter validation schema.

        Returns:
            A view decorator.
        """
        return view(
            url=url,
            method=["POST"],
            access=access,
            url_name=url_name,
            menu=menu,
            validate=validate,
            api=True,
        )

    def put(
        self,
        url: str,
        /,
        *,
        access: str | bool | Permission,
        url_name: str | None = None,
        menu: list[str] | None = None,  # @todo: dead code?
        validate: dict[str, Any] | None = None,
    ):
        """
        Decorate a PUT endpoint.

        Args:
            url: URL pattern relative to the application root.
            access: Access control rule.
            url_name: Optional URL name.
            menu: Optional menu entry metadata.
            validate: Optional request parameter validation schema.

        Returns:
            A view decorator.
        """
        return view(
            url=url,
            method=["PUT"],
            access=access,
            url_name=url_name,
            menu=menu,
            validate=validate,
            api=True,
        )

    def delete(
        self,
        url: str,
        /,
        *,
        access: str | bool | Permission,
        url_name: str | None = None,
        menu: list[str] | None = None,  # @todo: dead code?
        validate: dict[str, Any] | None = None,
    ):
        """
        Decorate a DELETE API endpoint.

        Args:
            url: URL pattern relative to the application root.
            access: Access control rule.
            url_name: Optional URL name.
            menu: Optional menu entry metadata.
            validate: Optional request parameter validation schema.

        Returns:
            A view decorator.
        """
        return view(
            url=url,
            method=["DELETE"],
            access=access,
            url_name=url_name,
            menu=menu,
            validate=validate,
            api=True,
        )


api = ViewAPI()
