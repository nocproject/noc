#!/usr/bin/env python

# Python modules
import os
import sys

# Adjust paths
d = os.path.dirname(sys.argv[0])
if not d:
    d = os.getcwd()
sys.path.insert(0, os.path.abspath(os.path.join(d, "..")))
sys.path.insert(0, d)

try:
    import settings  # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

from django.core.management import execute_from_command_line

if __name__ == "__main__":
    os.environ["DJANGO_SETTINGS_MODULE"] = "noc.settings"
    # Execute command
    from django.core.management.color import color_style
    from django.utils.encoding import smart_str
    try:
        execute_from_command_line(sys.argv)
    except OSError as e:
        sys.stderr.write(smart_str(color_style().ERROR("Error: %s\n" % e)))
