# ----------------------------------------------------------------------
# DocumentResource API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Union, Any, Optional, TypeVar, List, Dict, Callable
from http import HTTPStatus

# Third-party modules
from fastapi import HTTPException
from mongoengine.document import Document
from mongoengine.fields import ReferenceField
from mongoengine.queryset import QuerySet

# NOC modules
from noc.config import config
from noc.models import get_model
from noc.aaa.models.user import User
from noc.core.mongo.fields import ForeignKeyField, PlainReferenceField
from noc.core.typing import SupportsGetById
from .base import BaseResourceAPI


T = TypeVar("T", bound=Document)


class DocumentResourceAPI(BaseResourceAPI[T]):
    """
    Generic mongoengine-backed REST api.
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

    def get_total_items(self, user: User) -> int:
        return self.queryset(user).count()

    def get_items(
        self,
        user: User,
        limit: int = config.ui.max_rest_limit,
        offset: int = 0,
        transforms: Optional[List[Callable]] = None,
    ) -> List[T]:
        qs = self.queryset(user)
        if transforms:
            for t in transforms:
                qs = t(qs)
        qs = qs[offset : offset + limit]
        return qs

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
        def ensure_remote(remote: Union[SupportsGetById, str]) -> SupportsGetById:
            if isinstance(remote, str):
                return get_model(remote)
            return remote

        for name, field in self.model._fields.items():
            if isinstance(field, ForeignKeyField):
                self.add_ref_cleaner(field.name, ensure_remote(field.document_type))
            elif isinstance(field, ReferenceField):
                self.add_ref_cleaner(field.name, ensure_remote(field.document_type))
            elif isinstance(field, PlainReferenceField):
                self.add_ref_cleaner(field.name, ensure_remote(field.document_type))
