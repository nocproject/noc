# ---------------------------------------------------------------------
# Django settings
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging
import re
import os

# NOC modules
from noc.config import config

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "1"
DEBUG = False
TEMPLATE_DEBUG = DEBUG
ADMINS = []
MANAGERS = ADMINS
SERVER_EMAIL = None

# It is up to upstream server to check Host header
ALLOWED_HOSTS = ["*"]

# RDBMS settings
DATABASES = {
    "default": {
        "ENGINE": "noc.core.model.db",
        # "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": config.pg.db,
        "USER": config.pg.user,
        "PASSWORD": config.pg.password,
        "HOST": config.pg.addresses[0].host,
        "PORT": config.pg.addresses[0].port,
        "AUTOCOMMIT": True,
        "DISABLE_SERVER_SIDE_CURSORS": True,
        "OPTIONS": {"connect_timeout": config.pg.connect_timeout},
    }
}
ATOMIC_REQUESTS = False

TIME_ZONE = str(config.timezone)
LANGUAGE_CODE = config.language_code
# Set up date and time formats
DATE_FORMAT = config.date_time_formats.date_format
TIME_FORMAT = config.date_time_formats.time_format
MONTH_DAY_FORMAT = config.date_time_formats.month_day_format
YEAR_MONTH_FORMAT = config.date_time_formats.year_month_format
DATETIME_FORMAT = config.date_time_formats.datetime_format
# Set up date input formats
DATE_INPUT_FORMATS = ["%Y-%m-%d"]
if config.date_time_formats.date_format != DATE_INPUT_FORMATS[0]:
    DATE_INPUT_FORMATS.insert(
        0,
        re.sub(
            "[^./: ]", lambda match: "%%%s" % match.group(0), config.date_time_formats.date_format
        ),
    )
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
STATIC_URL = "/ui/pkg/django-media/"

# Make this unique, and don"t share it with anybody.
SECRET_KEY = config.secret_key

# The maximum size in bytes that a request body may be
# before a SuspiciousOperation (RequestDataTooBig) is raised.
DATA_UPLOAD_MAX_MEMORY_SIZE = config.web.max_upload_size

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = [
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
]
#
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
)
#
MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
    "noc.core.middleware.remoteuser.remote_user_middleware",
    "noc.core.middleware.tls.tls_middleware",
    "noc.core.middleware.extformat.ext_format_middleware",
]

ROOT_URLCONF = "noc.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": False,
        "DIRS": [".", "templates"],
        "OPTIONS": {"libraries": {"template_exists": "noc.templatetags.template_exists"}},
    }
]


INSTALLED_APPS = [
    "noc.aaa",
    "noc.main",
    "noc.dev",
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
    "noc.phone",
]

FORCE_SCRIPT_NAME = ""

# Available languages
_ = lambda s: s  # noqa. _ should be a lambda not a function
LANGUAGES = [("en", _("English")), ("ru", _("Russian")), ("pt_BR", _("Portuguese (BRAZIL)"))]

LOCALE_PATHS = ["locale"]
# Do not enforce lowercase tags
FORCE_LOWERCASE_TAGS = False
# Suppress deprecation warning. We don't use django's testing framework
TEST_RUNNER = None

# Disable SQL statement logging
logging.getLogger("django.db.backends").setLevel(logging.ERROR)
