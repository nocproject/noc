# ----------------------------------------------------------------------
# User model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
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
from django.contrib.postgres.fields import ArrayField

# NOC modules
from noc.config import config
from noc.core.model.base import NOCModel
from noc.core.model.decorator import on_delete_check
from noc.core.translation import ugettext as _
from noc.settings import LANGUAGES
from noc.main.models.avatar import Avatar
from noc.core.password.hasher import UNUSABLE_PASSWORD, check_password, make_password, must_change
from noc.core.password.check import check_password_policy
from .group import Group

id_lock = Lock()


@on_delete_check(
    check=[
        ("kb.KBEntryPreviewLog", "user"),
        ("aaa.UserContact", "user"),
        ("sa.UserAccess", "user"),
        ("kb.KBUserBookmark", "user"),
        ("main.Checkpoint", "user"),
        ("main.NotificationGroupUserSubscription", "user"),
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
    # Password policy
    change_at = models.DateTimeField("Change password at", blank=True, null=True)
    valid_from = models.DateTimeField("Password valid from", blank=True, null=True)
    valid_until = models.DateTimeField("Password valid until", blank=True, null=True)
    password_history = ArrayField(models.CharField(max_length=128), blank=True, null=True)

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

    def set_password(self, password: str, save: bool = True) -> None:
        """
        Set new password.

        Update password history when necessary.

        Args:
            password: Raw password.
            save: Save changes.

        Raises:
            ValueError: if password policy is violated
        """
        # Check password policy
        # Raises ValueError
        check_password_policy(
            min_password_len=config.login.min_password_len or None,
            min_password_uppercase=config.login.min_password_uppercase or None,
            min_password_lowercase=config.login.min_password_lowercase or None,
            min_password_numbers=config.login.min_password_numbers or None,
            min_password_specials=config.login.min_password_specials or None,
            history=self.password_history or None if config.login.password_history else None,
        )
        # Update history
        if (
            self.password
            and self.password != UNUSABLE_PASSWORD
            and config.login.password_history > 0
        ):
            hist = self.password_history or []
            hist.insert(0, self.password)
            self.password_history = hist[: config.login.password_history]
        # Update password ttl
        if config.login.password_ttl > 0:
            self.change_at = datetime.datetime.now() + datetime.timedelta(
                seconds=config.login.password_ttl
            )
        else:
            self.change_at = None
        # Calculate hash
        self.password = make_password(password)
        if save:
            self.save(update_fields=["password", "password_history", "change_at"])

    def check_password(self, password: str) -> bool:
        """
        Check if password is correct.

        Password policies must be checked separately.

        Args:
            password: Raw password.

        Returns:
            True: If password is valid.
            False: If password is invalid.
        """
        if self.password == UNUSABLE_PASSWORD:
            return False

        return check_password(password, self.password)

    def can_login_now(self) -> bool:
        """
        Check if user can login now.

        Validate password validity range.

        Returns:
            True: If user can log in.
            False: User cannot login.
        """
        now = datetime.datetime.now()
        if self.valid_from and self.valid_from > now:
            return False
        if self.valid_until and self.valid_until < now:
            return False
        return True

    def set_unusable_password(self):
        """
        Sets a value that will never be a valid hash.

        Doesn't changes a model. Must be saved explicitly.
        """
        self.password = UNUSABLE_PASSWORD

    def must_change_password(self) -> bool:
        """
        Check if user must change password.

        User can change password in case:
        * Password is expired.
        * Password hash is weak.

        Returns:
            True: if user must change password immediately.
        """
        if self.password == UNUSABLE_PASSWORD:
            return False
        # Time based
        if self.change_at:
            now = datetime.datetime.now()
            if self.change_at < now:
                return True
        return must_change(self.password)

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
