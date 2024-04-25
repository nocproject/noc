# ---------------------------------------------------------------------
# Create application skeleton
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import argparse
import os
import datetime
import re
from pathlib import Path

# Third-party modules
from django.db.models.fields import NOT_PROVIDED
from django.db.models import Model
from jinja2 import Template

# NOC modules
from noc.core.management.base import BaseCommand, CommandError
from noc.core.comp import smart_text


class Command(BaseCommand):
    """
    Create and initialize appliation skeleton
    """

    help = "Create application skeleton"

    def add_arguments(self, parser):
        parser.add_argument("--model", "-m", dest="model", help="List configs"),
        parser.add_argument(
            "--report", "-r", dest="report", choices=["simple"], help="Create Report"
        ),
        parser.add_argument("args", nargs=argparse.REMAINDER, help="List of generate App")

    rx_empty = re.compile("^ +\n", re.MULTILINE)

    # Model -> (Ext model type, widget, grid renderer)
    model_map = {
        "CharField": ("string", "textfield", None),
        "BooleanField": ("boolean", "checkboxfield", "NOC.render.Bool"),
        "NullBooleanField": ("boolean", "checkboxfield", "NOC.render.Bool"),
        "IntegerField": ("int", "numberfield", None),
        "TextField": ("string", "textarea", None),
        "DateField": ("date", "datefield", None),
        "DateTimeField": ("date", "datefield", None),
        "CIDRField": ("string", "textfield", None),
        "GenericIPAddressField": ("string", "textfield", None),
        "INETField": ("string", "textfield", None),
        "MACField": ("string", "textfield", None),
        "AutoCompleteTagsField": ("auto", "tagsfield", "NOC.render.Tags"),
        "TagsField": ("auto", "textfield", None),
    }

    # Document -> Ext type maps
    document_ext_type = {
        "StringField": "string",
        "BooleanField": "boolean",
        "IntField": "int",
        "LongField": "int",
        "FloatField": "float",
        "DateTimeField": "auto",
        "GeoPointField": "auto",
        "URLField": "string",
        "PlainReferenceField": "string",
        "ReferenceField": "string",
        "DictField": "auto",
        "RawDictField": "auto",
        "ListField": "auto",
        "EmbeddedDocumentListField": "auto",
        "ObjectIdField": "string",
        "UUIDField": "string",
        "BinaryField": "string",
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
        "ReferenceField": "textfield",
        "DictField": "textfield",
        "RawDictField": "textfield",
        "ListField": "textfield",
        "EmbeddedDocumentListField": "textfield",
        "ObjectIdField": "textfield",
        "UUIDField": "displayfield",
    }

    def compact(self, s):
        return self.rx_empty.sub("", s)

    def create_dir(self, path):
        if os.path.isdir(path):
            return
        self.print("    Creating directory %s ..." % path)
        try:
            os.mkdir(path)
            self.print("done")
        except OSError as e:
            self.print("failed:", e)
            raise CommandError("Failed to create directory")

    def create_file(self, path, data):
        self.print("    Writing file %s ..." % path)
        try:
            with open(path, "w") as f:
                f.write(data)
            self.print("done")
        except OSError as e:
            self.print("failed:", e)
            raise CommandError("Failed to write file")

    def to_js(self, data, indent=0):
        """
        Convert list of lists to JS list of dict
        :param data:
        :param indent:
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
                if isinstance(s, str):
                    return '"%s"' % s
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
        vars = {"year": str(datetime.datetime.now().year), "model": None}
        # Detect templateset
        templateset = "application"
        if options["model"]:
            templateset = "modelapplication"
            vars["model"] = options["model"]
        if options["report"]:
            templateset = {"simple": "simplereport"}[options["report"]]
        # Check templateset
        ts_root = os.path.join("templates", "newapp", templateset)
        if not os.path.isdir(ts_root):
            raise CommandError("Inconsistent template set %s" % templateset)
        # Fill templates
        for app in args:
            self.print("Creating skeleton for %s" % app)
            m, a = app.split(".", 1)
            if "." in a:
                raise CommandError("Application name must be in form <module>.<app>")
            if not os.path.isdir(Path("services", "web", "apps", m)):
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
                    fields = [{"type": "int", "name": "id"}]
                    for f in model._meta.fields:
                        if f.name == "id":
                            continue
                        fc = f.__class__.__name__
                        if fc in ("ForeignKey", "OneToOneField"):
                            # Foreign key
                            fr = f.remote_field.model
                            rc = "%s.%s" % (fr.__module__.split(".")[1], fr.__name__.lower())
                            fd = {
                                "type": "int",
                                "name": f.name,
                                "label": smart_text(f.verbose_name),
                                "blank": f.null,
                                "widget": "%s.LookupField" % rc,
                            }
                            fields += [fd]
                            fd = {"type": "string", "name": "%s__label" % f.name, "persist": False}
                            fields += [fd]
                            tv["requires"] += ["NOC.%s.LookupField" % rc]
                        else:
                            fd = {
                                "type": self.model_map[fc][0],
                                "name": f.name,
                                "label": smart_text(f.verbose_name),
                                "blank": f.null,
                                "widget": self.model_map[fc][1],
                            }
                            if f.default != NOT_PROVIDED and not callable(f.default):
                                fd["default"] = f.default
                            fields += [fd]
                    tv["base_class"] = "ExtModelApplication"
                else:
                    # Document
                    fields = [{"type": "string", "name": "id"}]
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
                            "label": smart_text(n),
                            "blank": not f.required,
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
                    if "default" in f and f["type"] != "auto":
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
            app_root = os.path.join("services", "web", "apps", m, a)
            if os.path.exists(app_root):
                raise CommandError("Application %s is already exists" % app)
            # Create apps/__init__.py if missed
            ui_root = os.path.join("ui", "web", m, a)
            # Create application directory
            self.create_dir(app_root)
            # Fill templates
            for dirpath, dirnames, files in os.walk(ts_root):
                dp = dirpath.split(os.sep)[3:]  # strip templates/newapp/<ts>/
                # Create directories
                for fn in files:
                    if fn == "DELETE":
                        continue
                    # Fill template
                    with open(os.path.join(dirpath, fn)) as f:
                        template = f.read()
                    content = Template(template).render(tv)
                    content = self.compact(content)
                    # Write template
                    if fn.endswith(".js.j2"):
                        pp = [ui_root] + dp[:-1]
                        dn = os.path.join(*pp)
                    else:
                        pp = [app_root] + dp
                        dn = os.path.join(*pp)
                    self.create_dir(dn)
                    self.create_file(os.path.join(dn, fn[:-3]), content)


if __name__ == "__main__":
    Command().run()
