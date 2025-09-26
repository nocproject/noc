# ----------------------------------------------------------------------
# ModelResource API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any, Optional, TypeVar, List, Dict, Callable
from http import HTTPStatus

# Third-party modules
from fastapi import HTTPException
from django.db.models import Model, QuerySet, ForeignKey, Count
from django.core.exceptions import FieldDoesNotExist

# NOC modules
from noc.config import config
from noc.models import get_model
from noc.aaa.models.user import User
from noc.core.model.fields import DocumentReferenceField
from noc.core.typing import SupportsGetById
from .base import BaseResourceAPI
from ...models.utils import SummaryItem


T = TypeVar("T", bound=Model)


class ModelResourceAPI(BaseResourceAPI[T]):
    """
    Generic Django-backed REST api.
    """

    model: T

    @classmethod
    def queryset(cls, user: User) -> QuerySet:
        """
        Get django's queryset adjusted to current user
        :param user:
        :return:
        """
        return cls.model.objects.all()

    def get_total_items(self, user: User, transforms: Optional[List[Callable]] = None) -> int:
        qs = self.queryset(user)
        if transforms:
            for t in transforms:
                qs = t(qs)
        return qs.count()

    def get_summary_items(
        self, user: User, field: str, transforms: Optional[List[Callable]] = None
    ) -> List[SummaryItem]:
        """
        Calculate total amount of items, satisfying criteria
        :param user:
        :param field:
        :param transforms:
        :return:
        """
        try:
            field = self.model._meta.get_field(field)
        except FieldDoesNotExist:
            raise HTTPException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=f"Unknown model field: {field}"
            )
        qs = self.queryset(user)
        if transforms:
            for t in transforms:
                qs = t(qs)
        return [
            SummaryItem(id=str(r[field.name]), label=str(r[field.name]), count=int(r["count"]))
            for r in qs.values(field.name).annotate(count=Count("id"))
        ]

    def get_items(
        self,
        user: User,
        sort: List[str],
        limit: int = config.ui.max_rest_limit,
        offset: int = 0,
        transforms: Optional[List[Callable]] = None,
    ) -> List[T]:
        # Start from initial restrictions
        qs = self.queryset(user)
        # Then apply transformations passed by query
        if transforms:
            for t in transforms:
                qs = t(qs)
        # Then apply sorting order
        qs = qs.order_by(*tuple(sort))
        # Finally, limit to selected frame
        return qs[offset : offset + limit]

    def get_item(self, id: str, user: User) -> Optional[T]:
        return self.queryset(user).filter(pk=id).first()

    def create_item(self, user: User, **kwargs) -> None:
        try:
            self.model(**kwargs).save()
        except Exception as e:
            raise HTTPException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=f"Failed to save: {e}"
            )

    def update_item(self, id: str, user: User, **kwargs) -> None:
        item = self.get_item(id=id, user=user)
        if not item:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
        for k, v in kwargs.items():
            setattr(item, k, v)
        try:
            item.save()
        except Exception as e:
            raise HTTPException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=f"Failed to save: {e}"
            )

    def delete_item(self, id: str, user: User) -> bool:
        item = self.get_item(id=id, user=user)
        if item:
            item.delete()
        return bool(item)

    def add_ref_cleaner(self, name: str, remote: SupportsGetById) -> None:
        def inner(value: Optional[Dict[str, Any]]) -> Optional[Any]:
            if not value:
                return None
            if not isinstance(value, Dict):
                raise ValueError("Must be dict")
            item = remote.get_by_id(value["id"])
            if not item:
                raise ValueError("Invalid reference")
            return item

        if not hasattr(remote, "get_by_id"):
            raise ValueError(
                f"{self.model.__class__.__name__}.{name} references to {remote.__class__.__name__} without get_by_id() method"
            )
        self.add_cleaner(name, inner)

    def setup_cleaners(self):
        for field in self.model._meta.local_fields:
            if isinstance(field, ForeignKey):
                self.add_ref_cleaner(field.name, field.remote_field.model)
            elif isinstance(field, DocumentReferenceField):
                remote = field.document
                if isinstance(remote, str):
                    remote = get_model(remote)
                self.add_ref_cleaner(field.name, remote)
