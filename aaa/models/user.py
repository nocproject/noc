# ----------------------------------------------------------------------
# User model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from threading import Lock
import operator
from typing import Optional

# Third-party modules
import cachetools
from django.db import models
from django.core import validators
from django.contrib.auth.hashers import check_password, make_password

# NOC modules
from noc.config import config
from noc.core.model.base import NOCModel
from noc.core.model.decorator import on_delete_check
from noc.core.translation import ugettext as _
from noc.settings import LANGUAGES
from noc.main.models.avatar import Avatar
from .group import Group

id_lock = Lock()


@on_delete_check(
    check=[
        ("kb.KBEntryPreviewLog", "user"),
        ("aaa.UserContact", "user"),
        ("sa.UserAccess", "user"),
        ("kb.KBUserBookmark", "user"),
        ("main.Checkpoint", "user"),
        ("main.NotificationGroupUser", "user"),
        ("main.ReportSubscription", "run_as"),
        ("ip.PrefixBookmark", "user"),
        ("kb.KBEntryHistory", "user"),
        ("ip.PrefixAccess", "user"),
        ("main.Favorites", "user"),
        ("bi.Dashboard", "owner"),
    ]
)
class User(NOCModel):
    class Meta(object):
        verbose_name = "User"
        verbose_name_plural = "Users"
        app_label = "aaa"
        # Point to django"s auth_user table
        db_table = "auth_user"
        ordering = ["username"]

    username = models.CharField(
        max_length=75,
        unique=True,
        help_text=_("Required. 30 characters or fewer. Letters, digits and " "@/./+/-/_ only."),
        validators=[
            validators.RegexValidator(r"^[\w.@+-]+$", _("Enter a valid username."), "invalid")
        ],
    )
    first_name = models.CharField(max_length=75, blank=True)
    last_name = models.CharField(max_length=75, blank=True)
    email = models.EmailField(blank=True)
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(
        default=True,
        help_text=_(
            "Designates whether this user should be treated as "
            "active. Unselect this instead of deleting accounts."
        ),
    )
    is_superuser = models.BooleanField(
        default=False,
        help_text=_(
            "Designates that this user has all permissions without " "explicitly assigning them."
        ),
    )
    date_joined = models.DateTimeField(default=datetime.datetime.now)
    groups = models.ManyToManyField(
        Group,
        blank=True,
        help_text=_(
            "The groups this user belongs to. A user will "
            "get all permissions granted to each of "
            "his/her group."
        ),
        related_name="user_set",
        related_query_name="user",
    )
    # Custom profile
    preferred_language = models.CharField(
        max_length=16, null=True, blank=True, default=config.language, choices=LANGUAGES
    )
    # Heatmap position
    heatmap_lon = models.FloatField(
        "Longitude", blank=True, null=True, default=config.web.heatmap_lon
    )
    heatmap_lat = models.FloatField(
        "Latitude", blank=True, null=True, default=config.web.heatmap_lat
    )
    heatmap_zoom = models.IntegerField(
        "Zoom", blank=True, null=True, default=config.web.heatmap_zoom
    )
    # Last login (Populated by login service)
    last_login = models.DateTimeField("Last Login", blank=True, null=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _contact_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.username

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id: int) -> Optional["User"]:
        return User.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_username(cls, name) -> Optional["User"]:
        return User.objects.filter(username=name).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_contact_cache"), lock=lambda _: id_lock)
    def get_by_contact(cls, contact) -> Optional["User"]:
        from .usercontact import UserContact

        uc = UserContact.objects.filter(params=contact).first()
        if uc:
            return uc.user
        return

    def is_authenticated(self) -> bool:
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return True

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """
        Returns a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """

        def setter(raw_password):
            self.set_password(raw_password)
            self.save(update_fields=["password"])

        return check_password(raw_password, self.password, setter)

    def set_unusable_password(self):
        # Sets a value that will never be a valid hash
        self.password = make_password(None)

    @property
    def contacts(self):
        from .usercontact import UserContact

        return [
            (c.time_pattern, c.notification_method, c.params)
            for c in UserContact.objects.filter(user=self)
        ]

    @property
    def active_contacts(self):
        """
        Get list of currently active contacts

        :returns: List of (method, params)
        """
        now = datetime.datetime.now()
        return [
            (c.notification_method, c.params) for c in self.contacts if c.time_pattern.match(now)
        ]

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def register_login(self, ts=None):
        """
        Register user login

        :param ts: Login timestamp
        :return:
        """
        ts = ts or datetime.datetime.now()
        self.last_login = ts
        self.save(update_fields=["last_login"])

    @property
    def avatar_url(self) -> Optional[str]:
        """
        Get user's avatar URL
        :return:
        """
        if not Avatar.objects.filter(user_id=str(self.id)).only("user_id").first():
            return None
        return f"/api/ui/avatar/{self.id}"

    @property
    def avatar_label(self) -> Optional[str]:
        """
        Get avatar's textual label
        :return:
        """
        r = []
        if self.first_name:
            r += [self.first_name[0].upper()]
        if self.last_name:
            r += [self.last_name[0].upper()]
        if not r:
            r += [self.username[:1].upper()]
        return "".join(r)
