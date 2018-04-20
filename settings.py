<<<<<<< HEAD
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
=======
# Django settings for noc project.
# Do not modify this file directly
# Edit etc/noc.conf instead
import ConfigParser
import sys
import os

# Check when started from notebook
if not os.path.isfile("etc/noc.defaults") and os.path.isfile("../etc/noc.defaults"):
    os.chdir("..")

# Load config
config = ConfigParser.SafeConfigParser()
config.read(["etc/noc.defaults", "etc/noc.conf"])
if not config.sections():
    # Called from autodoc
    # @todo: Remove?
    config.read(["../../../../etc/noc.defaults", "../../../../etc/noc.conf"])
# Load solutions's config
for sn in config.options("solutions"):
    if config.getboolean("solutions", sn):
        v, s = sn.split(".")
        cfg = os.path.join("solutions", v, s, "etc", "noc.")
        config.read([cfg + "defaults", cfg + "conf"])

DEBUG = config.getboolean("main", "debug")
TEMPLATE_DEBUG = DEBUG

## Set up admins
## @todo: remove
ADMINS = []
for a in config.get("main", "admin_emails").split(","):
    a = a.strip()
    if not a:
        continue
    n, d = a.split("@")
    ADMINS.append((n, a))

MANAGERS = ADMINS

SERVER_EMAIL = config.get("main", "server_email")

## RDBMS settings
DATABASE_ENGINE = config.get("database", "engine")
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": config.get("database", "name"),
        "USER": config.get("database", "user"),
        "PASSWORD": config.get("database", "password"),
        "HOST": config.get("database", "host"),
        "PORT": config.get("database", "port"),
        "TEST_NAME": "test_" + config.get("database", "name")
    }
}
DATABASE_SUPPORTS_TRANSACTIONS = True
## NoSQL settings
NOSQL_DATABASE_NAME = config.get("nosql_database", "name")
NOSQL_DATABASE_TEST_NAME = NOSQL_DATABASE_NAME + "_test"
NOSQL_DATABASE_USER = config.get("nosql_database", "user")
NOSQL_DATABASE_PASSWORD = config.get("nosql_database", "password")
NOSQL_DATABASE_HOST = config.get("nosql_database", "host")
NOSQL_DATABASE_PORT = config.get("nosql_database", "port")
NOSQL_DATABASE_REPLICA_SET = config.get("nosql_database", "replica_set")

TIME_ZONE = config.get("main", "timezone")
LANGUAGE_CODE = config.get("main", "language_code")
# Set up date and time formats
DATE_FORMAT = config.get("main", "date_format")
TIME_FORMAT = config.get("main", "time_format")
MONTH_DAY_FORMAT = config.get("main", "month_day_format")
YEAR_MONTH_FORMAT = config.get("main", "year_month_format")
DATETIME_FORMAT = config.get("main", "datetime_format")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

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
<<<<<<< HEAD
SECRET_KEY = config.secret_key
=======
SECRET_KEY = config.get("main", "secret_key")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = [
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader"
]
<<<<<<< HEAD
#
=======
# 
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
<<<<<<< HEAD
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

=======
    "django.contrib.messages.context_processors.messages",
    "noc.lib.app.setup_processor",
    )
#
MIDDLEWARE_CLASSES = [
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "noc.lib.middleware.HTTPBasicAuthMiddleware",
    "django.middleware.doc.XViewMiddleware",
    "django.middleware.transaction.TransactionMiddleware",
    "noc.lib.middleware.TLSMiddleware", # Thread local storage
    "noc.lib.middleware.ExtFormatMiddleware"
]

if config.get("authentication", "method") == "http":
    MIDDLEWARE_CLASSES += ["django.contrib.auth.middleware.RemoteUserMiddleware"]

>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
ROOT_URLCONF = "noc.urls"

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don"t forget to use absolute paths, not relative paths.
<<<<<<< HEAD
    ".",
    "templates",
    "django/contrib/admin/templates/"
)

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",  # Required by django auth
    "django.contrib.sites",
    "django.contrib.admin",
=======
    "local",
    ".",
    "templates"
)

CACHES = {
    "default": {
        "BACKEND": "noc.lib.cache.MongoDBCache"
    }
}

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.admin",
    "django.contrib.messages",
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    "south",
    # NOC modules
    "noc.main",
    "noc.project",
    "noc.wf",
    "noc.gis",
<<<<<<< HEAD
    "noc.crm",
=======
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
<<<<<<< HEAD
    "noc.maintenance",
    "noc.support",
    "noc.bi",
    "noc.sla",
    "noc.phone"
]
=======
    "noc.support"
]
# Populate list of locally-installed apps
apps = config.get("main", "installed_apps").strip()
if apps:
    INSTALLED_APPS += [app.strip() for app in apps.split(",")]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

FORCE_SCRIPT_NAME = ""

# Available languages
<<<<<<< HEAD
_ = lambda s: s # noqa. _ should be a lambda not a function
LANGUAGES = [
    ("en", _("English")),
    ("ru", _("Russian")),
    ("pt_BR", _("Portuguese (BRAZIL)"))
=======
_ = lambda s: s
LANGUAGES = [
    ("en", _("English")),
    ("ru", _("Russian")),
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
]

LOCALE_PATHS = ["locale"]

<<<<<<< HEAD
# SOUTH_AUTO_FREEZE_APP = False

AUTH_PROFILE_MODULE = "main.UserProfile"
#
# Determine WEB process
#
IS_WEB = sys.argv[0].endswith("/web/service.py")
=======
#SOUTH_AUTO_FREEZE_APP = False

AUTH_PROFILE_MODULE = "main.UserProfile"
##
## Determine WEB process
##
IS_WEB = ((len(sys.argv) >= 2 and sys.argv[0] == "manage.py" and
           sys.argv[1] in ["runserver", "test", "sync-perm", "shell"])
          or sys.argv[0].endswith("noc-web.py"))
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
IS_TEST = len(sys.argv) >= 2 and sys.argv[:2] == ["manage.py", "test"]

SKIP_SOUTH_TESTS = True
SOUTH_TESTS_MIGRATE = True
<<<<<<< HEAD
# Do not enforce lowercase tags
FORCE_LOWERCASE_TAGS = False
# Set up by test runner
TEST_FIXED_BEEF_BASE = None

# Disable SQL statement logging
=======
##
LOGIN_URL = "/main/auth/login/"  # @todo: remove
## Do not enforce lowercase tags
FORCE_LOWERCASE_TAGS = False
## Message application setup
MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"
## Store sessions in mongodb
SESSION_ENGINE = "mongoengine.django.sessions"
## X-Forwarded-Proto
if config.get("main", "x_forwarded_proto"):
    h = config.get("main", "x_forwarded_proto").upper().replace("-", "_")
    SECURE_PROXY_SSL_HEADER = ("HTTP_%s" % h, "https")
## Set up crashinfo limit
CRASHINFO_LIMIT = config.getint("main", "crashinfo_limit")
## Traceback order
TRACEBACK_REVERSE = config.get("main", "traceback_order") == "reverse"
## Fixed beefs directory
## Set up by test runner
TEST_FIXED_BEEF_BASE = None

LOG_MRT_COMMAND = None
if config.get("audit", "log_mrt_commands"):
    lmc = config.get("audit", "log_mrt_commands")
    if os.access(lmc, os.W_OK):
        LOG_MRT_COMMAND = lmc
    else:
        import sys
        sys.stderr.write(
            "Cannot write to '%s'. MRT command logging disabled\n" % lmc
        )
##
## Graphite settings
## @todo: Remove
GRAPHTEMPLATES_CONF = ""
LEGEND_MAX_ITEMS = 10
## Set up logging
## Disable SQL statement logging
import logging

>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
logging.getLogger("django.db.backends").setLevel(logging.ERROR)
