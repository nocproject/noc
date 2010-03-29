# Django settings for noc project.
# Do not modify this file directly
# Edit etc/noc.conf instead
import ConfigParser,sys

config=ConfigParser.SafeConfigParser()
config.read("etc/noc.defaults")
config.read("etc/noc.conf")

DEBUG = config.get("main","debug")
TEMPLATE_DEBUG = DEBUG

ADMINS=[]
for a in config.get("main","admin_emails").split(","):
    a=a.strip()
    if not a:
        continue
    n,d=a.split("@")
    ADMINS.append((n,a))

MANAGERS = ADMINS

SERVER_EMAIL      = config.get("main","server_email")

DATABASE_ENGINE   = config.get("database","engine")
DATABASE_NAME     = config.get("database","name")
DATABASE_USER     = config.get("database","user")
DATABASE_PASSWORD = config.get("database","password")
DATABASE_HOST     = config.get("database","host")
DATABASE_PORT     = config.get("database","port")

TIME_ZONE = config.get("main","timezone")
LANGUAGE_CODE = config.get("main","language_code")
# Set up date and time formats
DATE_FORMAT      = config.get("main","date_format")
TIME_FORMAT      = config.get("main","time_format")
MONTH_DAY_FORMAT = config.get("main","month_day_format")
YEAR_MONTH_FORMAT= config.get("main","year_month_format")
DATETIME_FORMAT  = config.get("main","datetime_format")

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = config.get("main","secret_key")

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)
# 
TEMPLATE_CONTEXT_PROCESSORS= (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'noc.lib.render.setup_processor',
    )
#
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'noc.main.middleware.TLSMiddleware', # Thread local storage
)

ROOT_URLCONF = 'noc.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    "local",
    ".",
    "template"
)

CACHE_BACKEND = 'locmem:///'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.databrowse',
    "south",
    
    "noc.main",
    "noc.sa",
    "noc.fm",
    "noc.pm",
    "noc.cm",
    "noc.ip",
    "noc.vc",
    "noc.dns",
    "noc.peer",
    "noc.kb",
)
# Populate list of locally-installed apps
apps=config.get("main","installed_apps").strip()
if apps:
    INSTALLED_APPS+=tuple([app.strip() for app in apps.split(",")])

FORCE_SCRIPT_NAME=""

#SOUTH_AUTO_FREEZE_APP = False

AUTH_PROFILE_MODULE="main.UserProfile"
##
## Determine WEB process
##
IS_WEB=(len(sys.argv)>=2 and sys.argv[0]=="manage.py" and sys.argv[1]=="runserver") or sys.argv[0].endswith("noc-fcgi.py")
##
## Coverage wrapper
##
TEST_RUNNER="noc.lib.test_runner.run_tests"
COVERAGE_REPORT_PATH="local/coverage_report"