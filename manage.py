#!/usr/bin/env python

# Python modules
import os
import sys
import site
import logging

# Adjust paths
d = os.path.dirname(sys.argv[0])
if not d:
    d = os.getcwd()
contrib = os.path.abspath(os.path.join(d, "contrib", "lib"))
sys.path.insert(0, contrib)
sys.path.insert(0, os.path.abspath(os.path.join(d, "..")))
sys.path.insert(0, d)
# Install eggs from contrib/lib
site.addsitedir(contrib)

try:
    import settings  # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)
from django.core.management import execute_from_command_line

if __name__ == "__main__":
    os.environ["DJANGO_SETTINGS_MODULE"] = "noc.settings"
    if (len(sys.argv) > 1 and
        sys.argv[1] not in ("test", "syncdb", "migrate", "debug-script",
                            "script-test", "topo-test", "collection",
                            "get-uuid")):
        # Initialize applications and models
        import noc.urls
    if len(sys.argv) > 1 and sys.argv[1] in ("runserver", "debug-script"):
        # Set loglevel to DEBUG
        #logging.root.setLevel(logging.DEBUG)
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(message)s')
    # Execute command
    from django.core.management.color import color_style
    from django.utils.encoding import smart_str
    try:
        execute_from_command_line(sys.argv)
    except OSError, why:
        sys.stderr.write(smart_str(color_style().ERROR("Error: %s\n" % why)))
