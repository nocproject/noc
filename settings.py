# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Django settings for NOC
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.config import config

DEBUG = False
TEMPLATE_DEBUG = False
ADMINS = []
MANAGERS = ADMINS
SERVER_EMAIL = None

# Postgres settings
DATABASE_ENGINE = config.pg.db_engine
DATABASES = {
    "default": {
        "ENGINE": config.pg.db_engine,
        "NAME": config.pg.db,
        "USER": config.pg.user,
        "PASSWORD": config.pg.password,
        "HOST": config.pg.host,
        "PORT": config.pg.port,
        "TEST_NAME": "test_" + config.pg.db,
        "OPTIONS": config.pg.db_options
    }
}
DATABASE_SUPPORTS_TRANSACTIONS = True

TIME_ZONE = config.timezone
LANGUAGE_CODE = config.language_code
# Set up date and time formats
DATE_FORMAT = config.date_format
TIME_FORMAT = config.time_format
MONTH_DAY_FORMAT = config.month_day_format
YEAR_MONTH_FORMAT = config.year_month_format
DATETIME_FORMAT = config.datetime_format

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
    "django.contrib.messages.context_processors.messages"
    )
#
MIDDLEWARE_CLASSES = [
    "noc.lib.middleware.WSGISetupMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.auth.middleware.RemoteUserMiddleware",
    "django.middleware.transaction.TransactionMiddleware",
    "noc.lib.middleware.TLSMiddleware",  # Thread local storage
    "noc.lib.middleware.ExtFormatMiddleware"
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.RemoteUserBackend'
]

ROOT_URLCONF = "noc.urls"

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don"t forget to use absolute paths, not relative paths.
    "local",
    ".",
    "templates",
    "django/contrib/admin/templates/"
)


INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.admin",
    "django.contrib.messages",
    "south",
    # NOC modules
    "noc.main",
    "noc.project",
    # "noc.wf",
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
    "noc.maintainance",
    "noc.support"
]

FORCE_SCRIPT_NAME = ""

# Available languages
_ = lambda s: s
LANGUAGES = [
    ("en", _("English")),
    ("ru", _("Russian")),
    ("pt_BR", _("Portuguese (BRAZIL)"))
]

LOCALE_PATHS = ["locale"]

#SOUTH_AUTO_FREEZE_APP = False

AUTH_PROFILE_MODULE = "main.UserProfile"

SKIP_SOUTH_TESTS = True
SOUTH_TESTS_MIGRATE = True
## Do not enforce lowercase tags
FORCE_LOWERCASE_TAGS = False
## Message application setup
MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"
## Store sessions in mongodb
SESSION_ENGINE = "mongoengine.django.sessions"
## X-Forwarded-Proto
SECORE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
## Set up logging
## Disable SQL statement logging
import logging

logging.getLogger("django.db.backends").setLevel(logging.ERROR)
