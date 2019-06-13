# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# User model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import six
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxLengthValidator


@six.python_2_unicode_compatible
class User(AbstractUser):
    class Meta(AbstractUser.Meta):
        verbose_name = "User"
        verbose_name_plural = "Users"
        app_label = "aaa"
        # Point to django's auth_user table
        db_table = "auth_user"
        abstract = False
        ordering = ["username"]

    def __str__(self):
        return self.username


# Enlarge username field size and replace validators
User._meta.get_field("username").max_length = User._meta.get_field("email").max_length
User._meta.get_field("username").validators = [
    v for v in User._meta.get_field("username").validators if not isinstance(v, MaxLengthValidator)
] + [MaxLengthValidator(User._meta.get_field("username").max_length)]
