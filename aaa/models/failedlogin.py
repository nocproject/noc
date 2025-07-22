# ----------------------------------------------------------------------
# FailedLogin model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from typing import Optional

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import StringField, DateTimeField, ListField, EmbeddedDocumentField
from pymongo import ReturnDocument

# NOC modules
from noc.config import config


class FailedLoginItem(EmbeddedDocument):
    meta = {"strict": False}

    timestamp = DateTimeField()
    message = StringField(required=False)

    def __str__(self) -> str:
        if self.message:
            return f"{self.timestamp!s}: {self.message}"
        return f"{self.timestamp!s}"


class FailedLogin(Document):
    meta = {
        "collection": "failedlogin",
        "strict": False,
        "auto_create_index": False,
    }

    username = StringField(required=True, unique=True)
    items = ListField(EmbeddedDocumentField(FailedLoginItem()))
    blocked_to = DateTimeField(required=False)

    def __str__(self) -> str:
        if self.blocked_to:
            return f"{self.username} ({len(self.items)} items), blocked to {self.blocked_to!s}"
        return f"{self.username} ({len(self.items)} items)"

    @classmethod
    def register(cls, username: str, *, message: Optional[str] = None) -> None:
        """
        Register failed login attempt.

        Args:
            username: User name.
            message: Optional message.
        """
        if not config.login.max_failed_attempts:
            return
        # Calculate retention time
        now = datetime.datetime.now()
        expire = now - config.login.failed_attempts_window
        # History item
        item = {"timestamp": now}
        if message:
            item["message"] = message
        # Update history
        r = FailedLogin._get_collection().find_one_and_update(
            {"username": username},
            {
                "$push": {"items": item},
                "$pull": {"items": {"timestamp": {"$gt": expire}}},
                "$setOnInsert": {"username": username},
            },
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        # Calculate failed logins
        failed_logins = sum(1 for item in r["items"] if item["timestamp"] >= expire)
        if failed_logins >= config.login.max_failed_attempts:
            FailedLogin._get_collection().update_one(
                {"_id": r["_id"]},
                {"$set": {"blocked_to": now + config.login.failed_attempts_cooldown}},
            )

    @classmethod
    def is_blocked_till(cls, username: str) -> Optional[datetime.datetime]:
        """
        Check if user is blocked.

        Args:
            username: User name.

        Returns:
            blocking expire time, if imposed. None if user is not blocked.
        """
        if not config.login.max_failed_attempts:
            return None
        now = datetime.datetime.now()
        r = FailedLogin._get_collection().find_one(
            {"username": username, "blocked_to": {"$gt": now}}, {"_id": 1, "blocked_to": 1}
        )
        if not r:
            return None  # No document
        return r["blocked_to"]
