# ---------------------------------------------------------------------
# NotificationGroup model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
import logging
import operator
from threading import Lock
from typing import Optional, Any
from collections.abc import Iterable
from pathlib import Path

# Third-party modules
from django.db.models import (
    TextField,
    CharField,
    ForeignKey,
    BooleanField,
    DateTimeField,
    UUIDField,
    CASCADE,
)
from django.contrib.postgres.fields import ArrayField
from django.db.models.query_utils import Q as d_Q
from pydantic import BaseModel, RootModel, model_validator
import cachetools

# NOC modules
from noc.core.model.base import NOCModel
from noc.core.model.fields import PydanticField, DocumentReferenceField
from noc.core.mx import (
    send_notification,
    NOTIFICATION_METHODS,
    MX_TO,
    MessageType,
    MessageMeta,
    get_subscriber_id,
    NotificationContact,
)
from noc.core.model.decorator import on_delete_check, on_save
from noc.core.change.decorator import change

from noc.core.prettyjson import to_json
from noc.core.path import safe_json_path
from noc.aaa.models.user import User
from noc.main.models.systemtemplate import SystemTemplate
from noc.main.models.template import Template
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.timepattern import TimePattern
from noc.models import get_model_id, get_model
from noc.config import config
from noc.settings import LANGUAGE_CODE

id_lock = Lock()
logger = logging.getLogger(__name__)


NOTIFICATION_DEFAULT_TEMPLATE = {
    "interface_status_change": "interface_status_change",
    "config_changed": "managed_object_config_change",
    "object_new": "managed_object_new",
    "object_deleted": "managed_object_delete",
    "version_changed": "managed_object_version_changed",
    "config_policy_violation": "managed_object_config_policy_violation",
}

NOTIFICATION_METHOD_CHOICES = [(x, x) for x in sorted(NOTIFICATION_METHODS)]
USER_NOTIFICATION_METHOD_CHOICES = NOTIFICATION_METHOD_CHOICES


class StaticMember(BaseModel):
    """
    Contact Members for notification Set
    """

    notification_method: str
    contact: str
    language: str | None = None
    time_pattern: int | None = None

    def get_contacts(self) -> list[NotificationContact]:
        """Build Notification Contact"""
        from noc.main.models.messageroute import MessageRoute

        r = []
        method, route = self.notification_method, None
        if method not in NOTIFICATION_METHODS:
            # Try Forward
            route = MessageRoute.get_by_id(method)
            if route:
                method, route = "webhook", str(route.id)
        for c in self.contact.split(","):
            r.append(
                NotificationContact(
                    contact=c,
                    method=method,
                    time_pattern=self.time_pattern,
                    route=route,
                ),
            )
        return r


StaticMembers = RootModel[list[StaticMember]]


class SubscriptionConditionItem(BaseModel):
    """
    Rules for Match message
        Attributes:
            labels: Match All labels in list
            resource_groups: Match Any resource group in List
            administrative_domain: Have Administrative domain in paths
    """

    labels: list[str] | None = None
    resource_groups: list[str] | None = None
    administrative_domain: int | None = None
    # profile, group, container, administrative_domain


class SubscriptionSettingItem(BaseModel):
    """
    Attributes:
        group: User group for apply settings
        allow_subscribe: Allow subscribe to group
        auto_subscription: Create subscription record
        notify_if_subscribed: Send notification if Subscription Changed
    """

    user: int | None = None
    group: int | None = None
    allow_subscribe: bool = False
    auto_subscription: bool = False
    notify_if_subscribed: bool = False

    @model_validator(mode="after")
    def check_user_group_match(self):
        if not self.user and not self.group:
            raise ValueError("User or Group must be set")
        return self


SubscriptionSettings = RootModel[list[SubscriptionSettingItem]]


SubscriptionConditions = RootModel[list[SubscriptionConditionItem]]


class MessageTypeItem(BaseModel):
    message_type: MessageType
    template: int | None = None
    language: str | None = None
    deny: bool = False


MessageTypes = RootModel[list[MessageTypeItem]]


@on_save
@change
@on_delete_check(
    check=[
        ("cm.ObjectNotify", "notification_group"),
        ("dns.DNSZone", "notification_group"),
        ("dns.DNSZoneProfile", "notification_group"),
        ("fm.AlarmTrigger", "notification_group"),
        ("fm.EventTrigger", "notification_group"),
        ("fm.AlarmRule", "actions__notification_group"),
        ("inv.InterfaceProfile", "default_notification_group"),
        ("main.ReportSubscription", "notification_group"),
        ("main.SystemNotification", "notification_group"),
        ("main.MessageRoute", "notification_group"),
        ("sa.ObjectNotification", "notification_group"),
        ("sa.ReactionRule", "notification_group"),
        ("peer.PeeringPoint", "prefix_list_notification_group"),
    ],
    delete=[
        ("main.NotificationGroupSubscription", "notification_group"),
        ("main.NotificationGroupUserSettings", "notification_group"),
    ],
)
class NotificationGroup(NOCModel):
    """
    Notification Groups
    """

    class Meta:
        verbose_name = "Notification Group"
        verbose_name_plural = "Notification Groups"
        app_label = "main"
        db_table = "main_notificationgroup"
        ordering = ["name"]

    _json_collection = {
        "collection": "templates",
        "json_collection": "main.notificationgroups",
        "json_unique_fields": ["name"],
    }

    name: str = CharField("Name", max_length=64, unique=True)
    uuid = UUIDField()
    description = TextField("Description", null=True, blank=True)
    message_register_policy = CharField(
        max_length=1,
        choices=[
            ("d", "Disable"),  # Direct
            ("a", "Any"),
            ("t", "By Types"),
        ],
        default="d",
        null=False,
        blank=False,
    )
    message_types: list[MessageTypeItem] = PydanticField(
        "Message Type Settings",
        schema=MessageTypes,
        blank=True,
        null=True,
        default=list,
    )
    static_members: list[StaticMember] | None = PydanticField(
        "Notification Contacts",
        schema=StaticMembers,
        blank=True,
        null=True,
        default=list,
    )
    subscription_settings: list[SubscriptionSettingItem] | None = PydanticField(
        "Subscription Settings",
        schema=SubscriptionSettings,
        blank=True,
        null=True,
        default=list,
    )
    # subscribed = ArrayField(CharField(max_length=100))
    subscription_to: list[str] = ArrayField(CharField(max_length=100), blank=True, null=True)
    conditions: list[SubscriptionConditionItem] | None = PydanticField(
        "Condition for match Notification Group",
        schema=SubscriptionConditions,
        blank=True,
        null=True,
        default=list,
    )

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: int) -> Optional["NotificationGroup"]:
        return NotificationGroup.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name: str) -> Optional["NotificationGroup"]:
        return NotificationGroup.objects.filter(name=name).first()

    @classmethod
    def get_groups_by_type(cls, message_type: MessageType) -> list["NotificationGroup"]:
        return list(
            NotificationGroup.objects.filter(message_types__message_type=message_type.value)
        )

    @classmethod
    def get_groups_by_user(cls, user: User) -> list["NotificationGroup"]:
        q = d_Q(subscription_settings__contains=[{"user": user.id}])
        for g in user.groups.filter():
            q |= d_Q(subscription_settings__contains=[{"group": g.id}])
        return list(NotificationGroup.objects.filter(q))

    @classmethod
    def get_user_settings(
        cls,
        group: "NotificationGroup",
        user: User,
    ) -> Optional["NotificationGroupUserSettings"]:
        """Getting user settings for group"""
        return NotificationGroupUserSettings.objects.filter(
            notification_group=group,
            user=user,
        ).first()

    def get_effective_template(
        self,
        message_type: MessageType,
        language: str | None = None,
    ) -> Optional["Template"]:
        """Return effective template for Notification Group"""
        for mt in self.message_types or []:
            mt = MessageTypeItem.model_validate(mt)
            if not mt.template or mt.message_type != message_type:
                continue
            if not language or not mt.language or (language and language == mt.language):
                return Template.get_by_id(mt.template)
        return Template.get_by_message_type(message_type, language)

    def get_subscription_setting(
        self,
        user: User,
    ) -> Optional["SubscriptionSettingItem"]:
        """"""
        for s in self.iter_subscription_settings:
            if (s.user and s.user == user.id) or (
                s.group and s.group in user.groups.values_list("id", flat=True)
            ):
                return s
        return None

    @classmethod
    def get_object_subscriptions(
        cls,
        o: Any,
        user: User | None = None,
    ) -> list["NotificationGroupSubscription"]:
        if not user:
            return NotificationGroupSubscription.objects.filter(
                model_id=get_model_id(o),
                instance_id=str(o.id),
            )
        return NotificationGroupSubscription.objects.filter(
            model_id=get_model_id(o),
            instance_id=str(o.id),
            watchers__contains=[get_subscriber_id(user)],
        )

    def get_user_subscription(
        self, o: Any, user: User
    ) -> Optional["NotificationGroupSubscription"]:
        """Getting subscription by user"""
        return NotificationGroupSubscription.objects.filter(
            notification_group=self,
            model_id=get_model_id(o),
            instance_id=str(o.id),
            watchers__contains=[get_subscriber_id(user)],
        ).first()

    @property
    def is_active(self) -> bool:
        """For cfgMX DataStream add"""
        return self.message_register_policy != "d"

    def iter_changed_datastream(self, changed_fields=None):
        if config.datastream.enable_cfgmxroute:
            yield "cfgmxroute", f"ng:{self.id}"

    # def on_save(self):
    #    self.ensure_subscriptions()
    def iter_conditions(self) -> Iterable[SubscriptionConditionItem]:
        """"""
        for s in self.conditions or []:
            yield SubscriptionConditionItem.model_validate(s)

    def get_route_config(self):
        """Return data for configured Router"""
        tt = ["*"]
        if self.message_types:
            tt = [x["message_type"] for x in self.message_types]
        r = {
            "id": str(self.id),
            "name": self.name,
            "type": tt,
            "order": 998,
            "action": "message",
            "notification_group": str(self.id),
            # r["render_template"] = str(self.render_template.id)
            "telemetry_sample": 0,
            "match": [],
        }
        if not self.conditions:
            return r
        for m in self.iter_conditions():
            c = {}
            if m.resource_groups:
                c[MessageMeta.GROUPS.value] = list(m.resource_groups)
            if m.labels:
                c[MessageMeta.LABELS.value] = list(m.labels)
            if m.administrative_domain:
                c[MessageMeta.ADM_DOMAIN.value] = m.administrative_domain
            if c:
                r["match"].append(c)
        return r

    def iter_static_members(self) -> Iterable[StaticMember]:
        for ngo in self.static_members or []:
            yield StaticMember.model_validate(ngo)

    @property
    def members(self) -> list[NotificationContact]:
        """List of (time pattern, method, params, language)"""
        contacts = []
        ts = datetime.datetime.now()
        # Collect other notifications
        for ngo in self.iter_static_members():
            for c in ngo.contact.split(","):
                if c not in contacts:
                    contacts.append(
                        NotificationContact(
                            contact=c,
                            method=ngo.notification_method,
                            time_pattern=ngo.time_pattern,
                        )
                    )
        if not self.subscription_settings:
            return contacts
        # Collect user notifications
        for ngu in self.notificationgroupusersettings_set.filter():
            if ngu.policy == "D" or ngu.suppress or ngu.policy == "W":
                continue
            if ngu.expired_at and ngu.expired_at > ts:
                continue
            if ngu.time_pattern and not ngu.time_pattern.match(ts):
                continue
            contacts += self.get_active_user_contacts(ngu.user, ts)
        return contacts

    def get_active_user_contacts(
        self, user: User, ts: datetime.datetime | None = None
    ) -> list["NotificationContact"]:
        """Getting Active user Contacts for send notification"""
        r = []
        us = self.get_user_settings(self, user)
        if not us:
            return r
        if us.time_pattern and not us.time_pattern.match(ts):
            return r
        for c in user.contacts:
            if c.time_pattern and c.time_pattern.match(ts):
                r.append(
                    NotificationContact(
                        contact=c.contact,
                        method=c.method,
                        time_pattern=c.time_pattern,
                        title_tag=us.title_tag,
                    )
                )
                break
        return r

    def get_active_contacts(
        self,
        obj: str | None = None,
        ts: datetime.datetime | None = None,
    ) -> list[NotificationContact]:
        now = ts or datetime.datetime.now()
        contacts = []
        for ngo in self.iter_static_members():
            contacts += ngo.get_contacts()
        watchers = []
        if not self.subscription_settings:
            return contacts
        # UserSubscriptionGroups
        for ngu in NotificationGroupUserSettings.objects.filter(
            notification_group=self,
            suppress=False,
        ):
            if ngu.policy == "D":
                continue
            if ngu.expired_at and ngu.expired_at > now:
                continue
            if ngu.policy == "W":
                watchers.append(get_subscriber_id(ngu.user))
                continue
            contacts += self.get_active_user_contacts(ngu.user, now)
        if not obj or not watchers:
            return contacts
        model_id, iid = obj.split(":")
        for s in NotificationGroupSubscription.objects.filter(
            model_id=model_id, instance_id=iid, watchers__overlap=watchers
        ).exclude(suppresses__overlap=watchers):
            for w in s.get_watchers(exclude_suppressed=True):
                contacts += self.get_active_user_contacts(w, now)
        return contacts

    @classmethod
    def get_user_subscriptions(cls, user: User, model_id: str) -> frozenset[str]:
        """Getting Subscription ids for model_id"""
        return frozenset(
            NotificationGroupSubscription.objects.filter(
                model_id=model_id, watchers__overlap=[get_subscriber_id(user)]
            )
            .exclude(suppresses__overlap=[get_subscriber_id(user)])
            .values_list("instance_id", flat=True)
        )

    @property
    def active_members(self) -> set[tuple[str, str, str | None]]:
        """List of currently active members: (method, param, language)"""
        return {(c.method, c.contact, c.language) for c in self.members}

    @property
    def languages(self) -> set[str]:
        """List of preferred languages for users"""
        return {x.language for x in self.members}

    @classmethod
    def get_effective_message(cls, messages, lang: str) -> str:
        for cl in (lang, LANGUAGE_CODE, "en"):
            if cl in messages:
                return messages[cl]
        return "Cannot translate message"

    @classmethod
    def send_notification(
        cls,
        method: str,
        address: str,
        subject: str,
        body: str | None = None,
        attachments: list[dict[str, Any]] | None = None,
    ):
        """
        Send notification message to MX service for processing
        Args:
            method: Method for sending message: mail, tg...
            address: Address to message
            subject: Notification Subject
            body: Notification body
            attachments:
        """
        from noc.main.models.messageroute import MessageRoute

        route = None
        if method not in NOTIFICATION_METHODS:
            logger.error("Unknown notification method: %s", method)
            route = MessageRoute.get_by_id(method)
            if route:
                method, route = "webhook", str(route.id)
            else:
                logger.error("Unknown notification method: %s", method)
                return
        logger.debug("Sending notification to %s via %s", address, method)
        send_notification(
            subject=subject,
            body=body,
            to=address,
            notification_method=method,
            attachments=attachments or [],
            fwd_to=route,
        )

    @classmethod
    def notify_user(
        cls,
        user: User,
        message_type: MessageType,
        subject: str | None = None,
        body: str | None = None,
        **kwargs,
    ):
        """"""

    def update_user_settings(
        self,
        user: User,
        policy: str,
        method: str | None = None,
        time_pattern: TimePattern | None = None,
        title_tag: str | None = None,
        expired_at: datetime.datetime | None = None,
        suppress: bool | None = None,
    ) -> "NotificationGroupUserSettings":
        """
        Update User settings for NotificationGroup
        Args:
            user: User instance
            policy: Notify policy:
                * D - Disable
                * A - Any messages
                * W - Only object watched
                * F ?
            method: Notification channel: mail, tg
            time_pattern: Time mask
            title_tag: String added to notification title
            expired_at: Disable send notification after timestamp
            suppress: Suppress send notification
        """
        # Check permission
        uss = self.get_user_settings(self, user)
        if not uss:
            uss = NotificationGroupUserSettings(notification_group=self, user=user)
        if uss.time_pattern != time_pattern:
            uss.time_pattern = time_pattern
        if uss.expired_at != expired_at:
            uss.expired_at = expired_at
        if uss.policy != policy:
            uss.policy = policy
        if uss.title_tag != title_tag:
            uss.title_tag = title_tag
        if uss.method != method:
            uss.method = method
        uss.save()
        return uss

    def get_effective_subscription(self, o: Any):
        """Getting subscription settings for Object"""
        # Group
        # Subscription
        # RemoteSystem

    def update_subscription(
        self,
        o: Any,
        watchers: list[Any],
        suppresses: list[Any],
        remote_system: RemoteSystem | None = None,
    ) -> "NotificationGroupSubscription":
        """Update notification subscription"""
        n = NotificationGroupSubscription.objects.get(
            notification_group=self,
            model_id=get_model_id(o),
            instance_id=str(o.id),
            remote_system=remote_system,
        )
        # get_contact
        n.watchers = [get_subscriber_id(w) for w in watchers]
        n.suppresses = [get_subscriber_id(w) for w in suppresses]
        for x in n.suppresses:
            if x not in n.watchers:
                n.watchers.append(x)
        n.save()
        return n

    def subscribe_object(self, o: Any, user: User):
        """Subscribe User to Group"""
        us = self.get_user_subscription(o, user)
        if us:
            return us
        c = get_subscriber_id(user)
        us = NotificationGroupSubscription.objects.filter(
            notification_group=self,
            model_id=get_model_id(o),
            instance_id=str(o.id),
            remote_system=None,
        ).first()
        if not us:
            us = NotificationGroupSubscription(
                notification_group=self,
                model_id=get_model_id(o),
                instance_id=str(o.id),
                watchers=[],
            )
        us.watchers.append(c)
        us.save()
        return us

    def unsubscribe_object(self, o: Any, user: User):
        """Unsubscribe User"""
        us = self.get_user_subscription(o, user)
        c = get_subscriber_id(user)
        # RemoteSystem
        if us and c in us.watchers:
            us.watchers.remove(c)
            NotificationGroupSubscription.objects.filter(id=us.id).update(
                watchers=us.watchers,
            )
        return us

    def supress_object(self, o: Any, user: User):
        """Supress Notification for subscription"""
        us = self.get_user_subscription(o, user)
        if not us:
            us = self.subscribe_object(o, user=user)
        c = get_subscriber_id(user)
        if us.suppresses and c not in us.suppresses:
            NotificationGroupSubscription.objects.filter(id=us.id).update(
                suppresses=(us.suppresses or []) + [c],
            )
        return us

    @property
    def iter_subscription_settings(self) -> Iterable[SubscriptionSettingItem]:
        """Subscription Settings"""
        for s in self.subscription_settings or []:
            yield SubscriptionSettingItem.model_validate(s)

    @classmethod
    def iter_object_subscription_settings(
        cls,
        o: Any,
        remote_system: RemoteSystem | None = None,
    ) -> Iterable["NotificationGroupSubscription"]:
        """
        Object Subscription settings
        Args:
            o: Object
            remote_system: RemoteSystem
        """
        # Group
        # Subscription
        # Remote
        # allow_edit
        # allow_suppress
        yield from NotificationGroupSubscription.objects.filter(
            model_id=get_model_id(o),
            instance_id=str(o.id),
        )

    def is_allowed_subscription(self, user: User) -> bool:
        groups = frozenset(user.groups.values_list("id", flat=True))
        for s in self.iter_subscription_settings:
            if s.user == user.id and s.allow_subscribe:
                return True
            if s.group in groups and s.allow_subscribe:
                return True
        return False

    # def ensure_subscriptions(self):
    #     """Ensure Subscription with settings"""
    #     print("Ensure Subscription")
    #     for s in self.iter_subscription_settings:
    #         if s.user:
    #             u = User.get_by_id(s.user)
    #             ng = self.get_subscription_by_user(u)
    #             if s.auto_subscription and not ng:
    #                 self.subscribe(u)
    #             elif not s.auto_subscription and ng:
    #                 self.unsubscribe(u)

    def register_message(
        self,
        message_type: str,
        ctx: dict[str, Any],
        meta: dict[str, Any],
        template: Optional["Template"] = None,
        attachments=None,
    ):
        """
        Register message on Group
        Attrs:
            message_type: Message Type
            ctx: Message Context Vars
            meta: Sender Metadata
            template: Template for render body
            attachments: Include attachments
        """

    def notify(self, subject, body, link=None, attachments=None, **kwargs):
        """
        Send message to active members
        Attrs:
            subject: Message subject
            body: Message body
            link: Optional link
            attachments: List of attachments. Each one is a dict
            with keys *filename* and *data*. *data* is the raw data
        """
        logger.debug("Notify group %s: %s", self.name, subject)
        if not isinstance(subject, dict):
            subject = {LANGUAGE_CODE: subject}
        if not isinstance(body, dict):
            body = {LANGUAGE_CODE: body}
        for method, params, lang in self.active_members:
            self.send_notification(
                method,
                params,
                self.get_effective_message(subject, lang),
                self.get_effective_message(body, lang),
                attachments,
            )

    @classmethod
    def group_notify(cls, groups, subject, body, link=None, delay=None, tag=None):
        """
        Send notification to a list of groups
        Prevent duplicated messages
        """
        if not subject and not body:
            return
        if subject is None:
            subject = ""
        if body is None:
            body = ""
        if not isinstance(subject, dict):
            subject = {LANGUAGE_CODE: subject}
        if not isinstance(body, dict):
            body = {LANGUAGE_CODE: body}
        ngs = set()
        lang = {}  # (method, params) -> lang
        for g in groups:
            for method, params, l in g.active_members:
                ngs.add((method, params))
                lang[(method, params)] = l
        for method, params in ngs:
            cls.send_notification(
                method,
                params,
                cls.get_effective_message(subject, lang[(method, params)]),
                cls.get_effective_message(body, lang[(method, params)]),
            )

    def iter_actions(
        self,
        message_type: str,
        meta: dict[MessageMeta, Any],
        ts: datetime.datetime | None = None,
    ) -> Iterable[tuple[str, dict[str, bytes], Optional["Template"]]]:
        """
        mx-compatible actions. Yields tuples of `stream`, `headers`
        """
        obj = None
        if MessageMeta.WATCH_FOR in meta:
            obj = meta[MessageMeta.WATCH_FOR].decode()
        for c in self.get_active_contacts(obj, ts=ts):
            yield c.method, {MX_TO: c.contact.encode()}, None

    @classmethod
    def render_message(
        cls, message_type: str, ctx: dict[str, Any], template: Optional["Template"] = None
    ) -> dict[str, str]:
        if not template and message_type in NOTIFICATION_DEFAULT_TEMPLATE:
            template = SystemTemplate.objects.filter(
                name=NOTIFICATION_DEFAULT_TEMPLATE[message_type]
            ).first()
        if not template:
            logger.warning("Not template for message type: %s", message_type)
            return ctx
        return {"subject": template.render_subject(**ctx), "body": template.render_body(**ctx)}

    @property
    def json_data(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "$collection": self._json_collection["json_collection"],
            "uuid": self.uuid,
            "description": self.description,
            "message_register_policy": self.message_register_policy,
            "message_types": [t.model_dump() for t in self.message_types],
        }

    def to_json(self) -> str:
        return to_json(
            self.json_data,
            order=[
                "name",
                "$collection",
                "uuid",
                "message_register_policy",
                "message_types",
            ],
        )

    def get_json_path(self) -> Path:
        return safe_json_path(self.name)


class NotificationGroupUserSettings(NOCModel):
    class Meta:
        verbose_name = "Notification Group User Subscription"
        verbose_name_plural = "Notification Group Users"
        app_label = "main"
        db_table = "main_notificationgroupusersettings"
        unique_together = [("notification_group_id", "user_id")]

    notification_group: NotificationGroup = ForeignKey(
        NotificationGroup, verbose_name="Notification Group", on_delete=CASCADE
    )
    time_pattern: TimePattern | None = ForeignKey(
        TimePattern, verbose_name="Time Pattern", on_delete=CASCADE, null=True, blank=True
    )
    user: User = ForeignKey(User, verbose_name="User", on_delete=CASCADE)
    method = CharField("Method", max_length=16, choices=USER_NOTIFICATION_METHOD_CHOICES)
    policy = CharField(
        max_length=1,
        choices=[
            ("D", "Disable"),  # Direct
            ("A", "Any"),
            ("W", "Only Watch"),
            ("F", "Favorites Only"),
        ],
        default="A",
        null=False,
        blank=False,
    )
    title_tag: str = CharField(max_length=30, blank=True)
    expired_at: datetime.datetime | None = DateTimeField(
        "Expired Subscription After", auto_now_add=False
    )
    suppress = BooleanField("Deactivate Subscription", default=False)

    def __str__(self):
        return f"{self.user.username}@{self.notification_group.name}: {self.time_pattern.name if self.time_pattern else ''}"

    @property
    def contacts(self) -> list[NotificationContact]:
        contacts = []
        for c in self.user.contacts:
            if self.method and c.method != self.method:
                continue
            if self.title_tag:
                contacts.append(
                    NotificationContact(
                        contact=c.contact,
                        method=c.method,
                        language=c.language,
                        time_pattern=c.time_pattern,
                        title_tag=self.title_tag,
                    )
                )
            else:
                contacts.append(c)
        return contacts


class NotificationGroupSubscription(NOCModel):
    class Meta:
        verbose_name = "Notification Group Watch Subscription"
        verbose_name_plural = "Notification Group Users"
        app_label = "main"
        db_table = "main_notificationgroupsubscription"
        unique_together = [("notification_group_id", "model_id", "instance_id", "remote_system")]

    notification_group: NotificationGroup = ForeignKey(
        NotificationGroup, verbose_name="Notification Group", on_delete=CASCADE
    )
    # On Group
    model_id = CharField(max_length=50)
    instance_id = CharField(max_length=100)
    watchers: list[str] = ArrayField(CharField(max_length=100), blank=True, null=True)
    suppresses: list[str] = ArrayField(CharField(max_length=100), blank=True, null=True)
    remote_system = DocumentReferenceField(RemoteSystem, null=True, blank=True)

    def is_match(self, meta: dict[MessageMeta, Any]):
        # time_pattern
        if f"m:{self.model_id}:{self.instance_id}" == meta[MessageMeta.WATCH_FOR]:
            return False
        if not self.watchers:
            return True
        if self.watchers and MessageMeta.FROM not in meta:
            return False
        return meta[MessageMeta.FROM] in self.watchers

    @property
    def contacts(self) -> list[NotificationContact]:
        contacts = []
        for w in self.get_watchers(exclude_suppressed=True):
            contacts += w.contacts
        return contacts

    def get_watchers(self, exclude_suppressed: bool = False):
        r = []
        for w in self.watchers:
            if exclude_suppressed and self.suppresses and w in self.suppresses:
                continue
            mid, oid = w.split(":")
            model = get_model(mid)
            w = model.get_by_id(oid)
            if w:
                r.append(w)
        return r
