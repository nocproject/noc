# Django settings for noc project.
# Do not modify this file directly
# All necessary configurations will be written by noc-tower
import ConfigParser
import sys
import os
from noc.core.config.base import config as cfg

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
if config.has_section("solutions"):
    for sn in config.options("solutions"):
        if config.getboolean("solutions", sn):
            v, s = sn.split(".")
            scfg = os.path.join("solutions", v, s, "etc", "noc.")
            config.read([scfg + "defaults", scfg + "conf"])

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

## Auto-detect appropriative database engine settings
if sys.argv[0].endswith("/discovery/service.py"):
    DB_ENGINE = "dbpool.db.backends.postgresql_psycopg2"
    DB_OPTIONS = {
        "MAX_CONNS": 1,
        "MIN_CONNS": 1
    }
    SOUTH_DATABASE_ADAPTER = "django.db.backends.postgresql_psycopg2"
else:
    DB_ENGINE = "django.db.backends.postgresql_psycopg2"
    DB_OPTIONS = {
        "ssl_mode": "disable"
    }

## RDBMS settings
DATABASE_ENGINE = DB_ENGINE
DATABASES = {
    "default": {
        "ENGINE": DB_ENGINE,
        "NAME": cfg.pg_db,
        "USER": cfg.pg_user,
        "PASSWORD": cfg.pg_password,
        "HOST": cfg.pg_connection_args["host"],
        "PORT": cfg.pg_connection_args["port"],
        "TEST_NAME": "test_" + cfg.pg_db,
        "OPTIONS": DB_OPTIONS
    }
}
DATABASE_SUPPORTS_TRANSACTIONS = True

TIME_ZONE = config.get("main", "timezone")
LANGUAGE_CODE = config.get("main", "language_code")
# Set up date and time formats
DATE_FORMAT = config.get("main", "date_format")
TIME_FORMAT = config.get("main", "time_format")
MONTH_DAY_FORMAT = config.get("main", "month_day_format")
YEAR_MONTH_FORMAT = config.get("main", "year_month_format")
DATETIME_FORMAT = config.get("main", "datetime_format")

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
SECRET_KEY = config.get("main", "secret_key")

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
    "django.contrib.messages.context_processors.messages",
    "noc.lib.app.setup_processor",
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
# Populate list of locally-installed apps
apps = config.get("main", "installed_apps").strip()
if apps:
    INSTALLED_APPS += [app.strip() for app in apps.split(",")]

FORCE_SCRIPT_NAME = ""

# Available languages
_ = lambda s: s
LANGUAGES = [
    ("en", _("English")),
    ("ru", _("Russian")),
]

LOCALE_PATHS = ["locale"]

#SOUTH_AUTO_FREEZE_APP = False

AUTH_PROFILE_MODULE = "main.UserProfile"
##
## Determine WEB process
##
IS_WEB = sys.argv[0].endswith("/web/service.py")
IS_TEST = len(sys.argv) >= 2 and sys.argv[:2] == ["manage.py", "test"]

SKIP_SOUTH_TESTS = True
SOUTH_TESTS_MIGRATE = True
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
## Set up logging
## Disable SQL statement logging
import logging

logging.getLogger("django.db.backends").setLevel(logging.ERROR)
