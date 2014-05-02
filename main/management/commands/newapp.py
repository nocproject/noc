# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Create application skeleton
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import os
import datetime
from optparse import make_option
import re
## Django modules
from django.core.management.base import BaseCommand, CommandError
from django.template import Template, Context
from django.db.models.fields import NOT_PROVIDED
from django.db.models import Model
## NOC modules
from noc.settings import INSTALLED_APPS
from noc.lib.nosql import Document


class Command(BaseCommand):
    """
    Create and initialize appliation skeleton
    """
    help = "Create application skeleton"
    option_list=BaseCommand.option_list+(
        make_option("--model", "-m", dest="model",
                    help="Create ModelApplication"),
        make_option("--report", "-r", dest="report",
                    choices=["simple"],
                    help="Create Report"))

    rx_empty = re.compile("^ +\n", re.MULTILINE)

    # Model -> (Ext model type, widget, grid renderer)
    model_map = {
        "CharField": ("string", "textfield", None),
        "BooleanField": ("boolean", "checkboxfield", "NOC.render.Bool"),
        "IntegerField": ("int", "numberfield", None),
        "TextField": ("string", "textarea", None),
        "DateField": ("date", "datefield", None),
        "DateTimeField": ("date", "datefield", None),
        "CIDRField": ("string", "textfield", None),
        "IPAddressField": ("string", "textfield", None),
        "INETField": ("string", "textfield", None),
        "MACField": ("string", "textfield", None),
        "AutoCompleteTagsField": ("auto", "tagsfield", "NOC.render.Tags"),
        "ColorField": ("int", "numberfield", None),
        "TagsField": ("auto", "textfield", None)
    }

    # Document -> Ext type maps
    document_ext_type = {
        "StringField": "string",
        "BooleanField": "boolean",
        "IntField": "int",
        "FloatField": "float",
        "DateTimeField": "auto",
        "GeoPointField": "auto",
        "URLField": "string",
        "PlainReferenceField": "string",
        "DictField": "auto",
        "RawDictField": "auto",
        "ListField": "auto",
        "ObjectIdField": "string",
        "UUIDField": "string"
    }
    # Document -> Ext type widgets
    document_ext_widget = {
        "StringField": "textfield",
        "BooleanField": "checkboxfield",
        "IntField": "numberfield",
        "FloatField": "numberfield",
        "DateTimeField": "textfield",
        "GeoPointField": "geofield",
        "URLField": "textfield",
        "PlainReferenceField": "textfield",
        "DictField": "textfield",
        "RawDictField": "textfield",
        "ListField": "textfield",
        "ObjectIdField": "textfield",
        "UUIDField": "displayfield"
    }

    def compact(self, s):
        return self.rx_empty.sub("", s)

    def create_dir(self, path):
        print "    Creating directory %s ..." % path,
        try:
            os.mkdir(path)
            print "done"
        except OSError, why:
            print "failed:", why
            raise CommandError("Failed to create directory")

    def create_file(self, path, data):
        print "    Writing file %s ..." % path,
        try:
            with open(path, "w") as f:
                f.write(data)
            print "done"
        except OSError, why:
            print "failed:", why
            raise CommandError("Failed to write file")

    def to_js(self, data, indent=0):
        """
        Convert list of lists to JS list of dict
        :param data:
        :return:
        """
        def js_f(data):
            """
            Convert list of pairs to JS dict
            :param data:
            :type data: list
            :return:
            """
            def js_v(s):
                """
                Convert python value to js
                :param s:
                :return:
                """
                if isinstance(s, basestring):
                    return "\"%s\"" % s
                elif isinstance(s, bool):
                    return "true" if s else "false"
                else:
                    return str(s)

            n = len(data)
            r = ["{"]
            for k, v in data:
                r += ["    %s: %s%s" % (k, js_v(v), "," if n > 1 else "")]
                n -= 1
            r += ["}"]
            return r

        n = len(data)
        r = []
        for d in data:
            r += js_f(d)
            if n > 1:
                r[-1] += ","
            n -= 1
        s = "    " * (indent + 1)
        r = ["["] + [s + x for x in r] + ["    " * indent + "]"]
        return "\n".join(r)

    def handle(self, *args, **options):
        # Template variables
        vars = {
            "year": str(datetime.datetime.now().year),
            "model": None
        }
        # Detect templateset
        templateset = "application"
        if options["model"]:
            templateset = "modelapplication"
            vars["model"] = options["model"]
        if options["report"]:
            templateset = {
                "simple": "simplereport"
            }[options["report"]]
        # Check templateset
        ts_root = os.path.join("main", "templates", "newapp", templateset)
        if not os.path.isdir(ts_root):
            raise CommandError("Inconsistent template set %s" % templateset)
        # Get installed modules
        modules = set([a[4:] for a in INSTALLED_APPS if a.startswith("noc.")])
        # Fill templates
        for app in args:
            print "Creating skeleton for %s" % app
            m, a = app.split(".", 1)
            if "." in a:
                raise CommandError("Application name must be in form <module>.<app>")
            if m not in modules:
                raise CommandError("Invalid module: %s" % m)
            # Fill template variables
            tv = vars.copy()
            tv["module"] = m
            tv["app"] = a
            # Initialize model if necessary
            if tv["model"]:
                tv["requires"] = ["NOC.%s.%s.Model" % (m, tv["model"].lower())]
                tv["modelimport"] = "noc.%s.models.%s" % (m, a)
                models = __import__(tv["modelimport"], {}, {}, tv["model"])
                model = getattr(models, tv["model"])
                if model is None:
                    tv["modelimport"] = "noc.%s.models" % m
                    models = __import__(tv["modelimport"], {}, {}, "*")
                    model = getattr(models, tv["model"])
                if issubclass(model, Model):
                    # Model
                    fields = [{
                        "type": "int",
                        "name": "id"
                    }]
                    for f in model._meta.fields:
                        if f.name == "id":
                            continue
                        fc = f.__class__.__name__
                        if fc in ("ForeignKey", "OneToOneField"):
                            # Foreign key
                            fr = f.rel.to
                            rc = "%s.%s" % (fr.__module__.split(".")[1],
                                            fr.__name__.lower())
                            fd = {
                                "type": "int",
                                "name": f.name,
                                "label": unicode(f.verbose_name),
                                "blank": f.null,
                                "widget": "%s.LookupField" % rc
                            }
                            fields += [fd]
                            fd = {
                                "type": "string",
                                "name": "%s__label" % f.name,
                                "persist": False
                            }
                            fields += [fd]
                            tv["requires"] += ["NOC.%s.LookupField" % rc]
                        else:
                            fd = {
                                "type": self.model_map[fc][0],
                                "name": f.name,
                                "label": unicode(f.verbose_name),
                                "blank": f.null,
                                "widget": self.model_map[fc][1]
                            }
                            if f.default != NOT_PROVIDED:
                                fd["default"] = f.default
                            fields += [fd]
                    tv["base_class"] = "ExtModelApplication"
                else:
                    # Document
                    fields = [{
                        "type": "string",
                        "name": "id"
                    }]
                    for n, f in model._fields.items():
                        if n == "id":
                            continue
                        fc = f.__class__.__name__
                        if fc == "ForeignKeyField":
                            ft = "int"
                        else:
                            ft = self.document_ext_type[fc]
                        fd = {
                            "type": ft,
                            "name": n,
                            "label": unicode(n),
                            "blank": not f.required
                        }
                        if f.default:
                            fd["default"] = f.default
                        fields += [fd]
                    tv["base_class"] = "ExtDocApplication"
                tv["fields"] = fields
            # Format fields for models
            if "fields" in tv:
                # Model fields
                fields = []
                for f in tv["fields"]:
                    ff = [("name", f["name"]), ("type", f["type"])]
                    if "default" in f:
                        ff += [("defaultValue", f["default"])]
                    if "persist" in f:
                        ff += [("persist", f["persist"])]
                    fields += [ff]
                tv["js_fields"] = self.to_js(fields, 1)
                # Form fields
                form_fields = []
                for f in [x for x in tv["fields"] if "widget" in x]:
                    ff = [("name", f["name"]), ("xtype", f["widget"])]
                    if f["widget"] == "checkboxfield":
                        ff += [("boxLabel", f["label"])]
                    else:
                        ff += [("fieldLabel", f["label"])]
                    ff += [("allowBlank", f["blank"])]
                    form_fields += [ff]
                tv["js_form_fields"] = self.to_js(form_fields, 1)
            # Check applications is not exists
            app_root = os.path.join(m, "apps", a)
            if os.path.exists(app_root):
                raise CommandError("Application %s is already exists" % app)
            # Create apps/__init__.py if missed
            apps_root = os.path.join(m, "apps")
            if not os.path.exists(apps_root):
                self.create_dir(apps_root)
            apps_init = os.path.join(apps_root, "__init__.py")
            if not os.path.exists(apps_init):
                self.create_file(apps_init, "")
            # Create application directory
            self.create_dir(app_root)
            # Fill templates
            for dirpath, dirnames, files in os.walk(ts_root):
                dp = dirpath.split(os.sep)[4:]  # strip main/templates/newapp/<ts>/
                # Create directories
                for d in dirnames:
                    p = [app_root] + dp + [d]
                    self.create_dir(os.path.join(*p))
                for fn in files:
                    if fn == "DELETE":
                        continue
                    # Fill template
                    with open(os.path.join(dirpath, fn)) as f:
                        template = f.read()
                    content = Template(template).render(Context(tv))
                    content = self.compact(content)
                    # Write template
                    p = [app_root] + dp + [fn]
                    self.create_file(os.path.join(*p), content)
