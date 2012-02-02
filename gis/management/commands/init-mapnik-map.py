# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Initialize OpenStreetMap MAP layer
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import os
import shutil
from optparse import make_option
from xml.parsers import expat
## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.gis.models import *

TAG = 0
ATTR = 1
CHILDREN = 2
CDATA = 3

ESRI_EXT = (".shp", ".shx", ".dbf", ".prj", ".sbn", ".sbx", ".shp.xml", ".cpg")


class Command(BaseCommand):
    help = "Initialize Mapnik XML MAP"

    option_list = BaseCommand.option_list + (
        make_option("-n", "--name", dest="name"),
        make_option("-p", "--prefix", dest="prefix"),
        make_option("-f", "--force", dest="force",
                    action="store_true", default=False)
    )

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError("Missed .xml path")
        self.name = options["name"]
        if not self.name:
            raise CommandError("Map name is empty.")
        self.prefix = options["prefix"]
        if not self.prefix:
            raise CommandError("Prefix is empty")
        self.srs_cache = {}  # proj4text -> SRS
        if options["force"]:
            self.force_cleanup()
        self.init_mapnik_map(options["name"], args[0])

    def force_cleanup(self):
        """
        Remove previous import from database
        :return:
        """
        print "Cleaning up"
        p = self.prefix + "-"
        Map.objects.filter(name=self.name).delete()
        Layer.objects.filter(name__startswith=p).delete()
        Style.objects.filter(name__startswith=p).delete()
        FontSet.objects.filter(name__startswith=p).delete()

    def init_mapnik_map(self, map_name, xml_path):
        """
        Upload OSM meta into database
        :param map_name:
        :param xml_path:
        :return:
        """
        self.root = None
        self.ctx = []
        # Create parser and parse XML
        self.parser = expat.ParserCreate()
        self.parser.SetBase(os.path.dirname(xml_path))
        self.setup_parser(self.parser)
        with open(xml_path) as f:
            self.parser.ParseFile(f)
        # Upload to database
        for tag, attrs, children, cdata in self.root[CHILDREN]:
            if tag == "fontset":
                self.sync_fontset(attrs, children)
            elif tag == "style":
                self.sync_style(attrs, children)
            elif tag == "layer":
                self.sync_layer(attrs, children)
            else:
                raise CommandError("Unknown tag: %s" % tag)
        self.sync_map(self.root[ATTR])

    def prefixed_name(self, name):
        return "%s-%s" % (self.prefix, name)

    def get_SRS(self, proj):
        """
        Find SRS by projection
        @todo: Universal proj to SRS matcher
        :param proj:
        :return:
        """
        if proj in self.srs_cache:
            return self.srs_cache[proj]
        srs = SRS.objects.get(srid=900913)  # proj4text=proj)
        self.srs_cache[proj] = srs
        return srs

    def setup_parser(self, parser):
        """
        Set up expat xml parser
        :param parser:
        :return:
        """
        parser.UseForeignDTD(True)
        parser.SetParamEntityParsing(expat.XML_PARAM_ENTITY_PARSING_ALWAYS)
        parser.StartElementHandler = self.expat_start_element
        parser.EndElementHandler = self.expat_end_element
        parser.CharacterDataHandler = self.expat_cdata
        parser.ExternalEntityRefHandler = self.expat_external_entity_ref
        return parser

    def expat_start_element(self, name, attrs):
        e = [name.lower(), attrs, [], ""]
        if self.root is None:
            self.root = e
            self.ctx = [e]
        else:
            self.ctx[-1][CHILDREN] += [e]
            self.ctx += [e]

    def expat_end_element(self, name):
        self.ctx[-1][CDATA] = self.ctx[-1][CDATA].strip()  # Strip CDATA
        self.ctx.pop(-1)

    def expat_cdata(self, data):
        self.ctx[-1][CDATA] += data

    def expat_external_entity_ref(self, context, base, system_id, public_id):
        if base and system_id:
            path = os.sep.join([base, system_id])
            if not os.path.isfile(path):
                t_path = path + ".template"
                if not os.path.isfile(t_path):
                    raise CommandError("Template not found: %s" % t_path)
                self.expand_inc_template(t_path, path)
            subparser = self.parser.ExternalEntityParserCreate(context)
            subparser.SetBase(os.path.dirname(path))
            self.setup_parser(subparser)
            with open(path) as f:
                subparser.ParseFile(f)
        return 1

    def expand_inc_template(self, t_path, path):
        """
        Expand OSM templates (.xml.inc.template to .xml.inc)
        :param t_path:
        :param path:
        :return:
        """
        with open(t_path) as f:
            data = f.read()
        data = data % {
            # Settings
            "symbols": "symbols",
            "epsg": "900913",
            "world_boundaries": "world_boundaries",
            "prefix": "gis_osm",
            # Database
            "dbname": "",  # Auto-filled by map_to_xml
            "host": "",
            "port": "",
            "user": "",
            "password": "",
            "estimate_extent": "false",
            "extent": "-20037508,-19929239,20037508,19929239"
        }
        with open(path, "w") as f:
            f.write(data)

    def install_file(self, path, ext=None):
        """
        Copy file to local/gis/<prefix> and return new path
        :return:
        """
        if ext:
            # Try to remove extension
            for e in ext:
                if path.endswith(e):
                    path = path[:-len(e)]
                    break
        fp = os.path.join(self.parser.GetBase(), path)
        fl = []
        if os.path.exists(fp):
            fl = [path]
        elif "[length]" in path:
            fl = [name
                  for name in [path.replace("[length]", str(i))
                               for i in range(1, 9)]
                  if os.path.exists(os.path.join(self.parser.GetBase(), name))]
        elif ext:
            fl = [path + e for e in ext if os.path.exists(fp + e)]
        if not fl:
            raise CommandError("File not found: %s" % fp)
        # Install files
        for f in fl:
            fp = os.path.join(self.parser.GetBase(), f)
            tp = os.path.join("local", "gis", self.prefix, f)
            if not os.path.exists(tp):
                print "    copying %s" % f
                d = os.path.dirname(tp)
                if not os.path.exists(d):
                    os.makedirs(d)
                shutil.copyfile(fp, tp)
        return os.path.join("local", "gis", self.prefix, path)

    def sync_fontset(self, attrs, children):
        def face_name(x):
            if "face_name" in x:
                return x["face_name"]
            else:
                return x["face-name"]

        fn = self.prefixed_name(attrs["name"])
        if FontSet.objects.filter(name=fn).count() > 0:
            return
        print "Installing FontSet %s" % fn
        FontSet(
            name=fn,
            description="OpenStreetMap '%s' font set" % attrs["name"],
            fonts=[face_name(c[ATTR]) for c in children if c[TAG] == "font"]
        ).save()

    def sync_style(self, attrs, children):
        sn = self.prefixed_name(attrs["name"])
        if Style.objects.filter(name=sn).count() > 0:
            return
        print "Installng style %s" % sn
        rules = []
        for ctag, cattrs, cchildren, ccdata in children:
            if ctag == "rule":
                minscale_zoom = None
                maxscale_zoom = None
                rule_filter = None
                symbolizers = []
                for cctag, ccattrs, ccchildren, cccdata in cchildren:
                    if cctag == "maxscaledenominator":
                        maxscale_zoom = int(cccdata)
                    elif cctag == "minscaledenominator":
                        minscale_zoom = int(cccdata)
                    elif cctag == "filter":
                        if cccdata:
                            rule_filter = cccdata
                    elif cctag.endswith("symbolizer"):
                        s = {"type": cctag[:-10]}
                        if cccdata:
                            s["cdata"] = cccdata
                        for ccctag, cccattrs, cccchildren,\
                                ccccdata in ccchildren:
                            if ccctag == "cssparameter":
                                s[cccattrs["name"]] = ccccdata
                        for k, v in ccattrs.items():
                            k = k.replace("_", "-")
                            if k == "fontset-name":
                                v = self.prefixed_name(v)
                            elif k == "file":
                                v = self.install_file(v)
                            s[k] = v
                        symbolizers += [s]
                rules += [Rule(minscale_zoom=minscale_zoom,
                               maxscale_zoom=maxscale_zoom,
                               rule_filter=rule_filter,
                               symbolizers=symbolizers)]
            else:
                raise CommandError("Invalid tag: %s" % ctag)
        # Save style
        Style(name=sn, rules=rules).save()

    def sync_layer(self, attrs, children):
        ln = self.prefixed_name(attrs["name"])
        if Layer.objects.filter(name=ln).count() > 0:
            return
        print "Installing layer %s" % ln
        datasource = {}
        styles = []
        for ctag, cattrs, cchildren, ccdata in children:
            if ctag == "stylename":
                styles += [self.prefixed_name(ccdata)]
            elif ctag == "datasource":
                for cctag, ccattrs, ccchildren, cccdata in cchildren:
                    if cctag == "parameter":
                        datasource[ccattrs["name"]] = cccdata
                    else:
                        raise CommandError("Invalid tag: %s" % cctag)
            else:
                raise CommandError("Invalid data: %s" % ctag)
        # Save all shapes
        if datasource["type"] == "shape":
            datasource["file"] = self.install_file(datasource["file"],
                                                   ESRI_EXT)
        # Save layer
        Layer(
            name=ln,
            is_active=attrs.get("status") == "on",
            srs=self.get_SRS(attrs["srs"]),
            styles=styles,
            datasource=datasource
        ).save()

    def sync_map(self, attrs):
        if Map.objects.filter(name=self.name).count() > 0:
            return
        print "Installing map %s" % self.name
        Map(
            name=self.name,
            is_active=True,
            srs=self.get_SRS(attrs["srs"]),
            layers=[self.prefixed_name(c[ATTR]["name"])
                    for c in self.root[CHILDREN] if c[TAG] == "layer"]
        ).save()
