# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Django settings
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import sys
import logging
from noc.config import config
if config.features.pypy:
    from psycopg2cffi import compat
    compat.register()

DEBUG = False
TEMPLATE_DEBUG = DEBUG
ADMINS = []
MANAGERS = ADMINS
SERVER_EMAIL = None

# RDBMS settings
DATABASES = {
    "default": {
        "ENGINE": "noc.core.model.db",
        "NAME": config.pg.db,
        "USER": config.pg.user,
        "PASSWORD": config.pg.password,
        "HOST": config.pg.addresses[0].host,
        "PORT": config.pg.addresses[0].port,
        "TEST_NAME": "test_" + config.pg.db,
        "OPTIONS": {
            "autocommit": True,
            "connect_timeout": config.pg.connect_timeout
        }
    }
}

SOUTH_DATABASE_ADAPTERS = {
    "default": "south.db.postgresql_psycopg2"
}

TIME_ZONE = config.timezone
LANGUAGE_CODE = config.language_code
# Set up date and time formats
DATE_FORMAT = config.date_time_formats.date_format
TIME_FORMAT = config.date_time_formats.time_format
MONTH_DAY_FORMAT = config.date_time_formats.month_day_format
YEAR_MONTH_FORMAT = config.date_time_formats.year_month_format
DATETIME_FORMAT = config.date_time_formats.datetime_format

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ""

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = ""

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
STATIC_URL = "/media/"

# Make this unique, and don"t share it with anybody.
SECRET_KEY = config.secret_key

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = [
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader"
]
#
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "noc.core.middleware.context.messages"
)
#
MIDDLEWARE_CLASSES = [
    "django.middleware.common.CommonMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "noc.core.middleware.remoteuser.RemoteUserMiddleware",
    "noc.core.middleware.tls.TLSMiddleware",  # Thread local storage
    "noc.core.middleware.extformat.ExtFormatMiddleware"
]

ROOT_URLCONF = "noc.urls"

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don"t forget to use absolute paths, not relative paths.
    ".",
    "templates",
    "django/contrib/admin/templates/"
)

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",  # Required by django auth
    "django.contrib.sites",
    "django.contrib.admin",
    "south",
    # NOC modules
    "noc.main",
    "noc.project",
    "noc.wf",
    "noc.gis",
    "noc.crm",
    "noc.inv",
    "noc.sa",
    "noc.fm",
    "noc.pm",
    "noc.cm",
    "noc.ip",
    "noc.vc",
    "noc.dns",
    "noc.peer",
    "noc.kb",
    "noc.maintenance",
    "noc.support",
    "noc.bi",
    "noc.sla",
    "noc.phone"
]

FORCE_SCRIPT_NAME = ""

# Available languages
_ = lambda s: s # noqa. _ should be a lambda not a function
LANGUAGES = [
    ("en", _("English")),
    ("ru", _("Russian")),
    ("pt_BR", _("Portuguese (BRAZIL)"))
]

LOCALE_PATHS = ["locale"]

# SOUTH_AUTO_FREEZE_APP = False

AUTH_PROFILE_MODULE = "main.UserProfile"
#
# Determine WEB process
#
IS_WEB = sys.argv[0].endswith("/web/service.py")
IS_TEST = len(sys.argv) >= 2 and sys.argv[:2] == ["manage.py", "test"]

SKIP_SOUTH_TESTS = True
SOUTH_TESTS_MIGRATE = True
# Do not enforce lowercase tags
FORCE_LOWERCASE_TAGS = False
# Set up by test runner
TEST_FIXED_BEEF_BASE = None

# Disable SQL statement logging
logging.getLogger("django.db.backends").setLevel(logging.ERROR)
