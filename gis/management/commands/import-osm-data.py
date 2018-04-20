# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Import OpenStreetMap spatial data from
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
from optparse import make_option
from urllib2 import urlopen
import os
import subprocess
import re
## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.settings import config
from noc.lib.db import check_postgis, check_srs
from noc.lib.fileutils import search_path, temporary_file
from noc.gis.models import Area
from noc.gis.geo import MIN_ZOOM, MAX_ZOOM
from noc.gis.utils import parse_osm_bounds


class Command(BaseCommand):
    help = "Import OpenStreetMap spatial data"

    option_list = BaseCommand.option_list + (
        make_option("-b", "--bbox", dest="bbox"),
        make_option("-f", "--file", dest="file"),
        make_option("-a", "--area", dest="area")
        )

    OSM_API_URL = "http://api.openstreetmap.org/api/0.6/map?bbox="

    rx_bounds = re.compile(r"(<bounds\s+(.+?)\s*/>)", re.MULTILINE)
    rx_bound_box = re.compile(r'<bound\s+box="([^\"]+)"')

    def handle(self, *args, **options):
        db_name = config.get("database", "name")
        # Check PostGIS is enabled
        if not check_postgis():
            raise CommandError("PostGIS is not installed. "\
                               "Install PostGIS into '%s' database" % db_name)
            # Check spatial references are loaded
        if not check_srs():
            raise CommandError("Spatial references not loaded. "\
                               "Load spatial_ref_sys.sql into "\
                               "'%s' database" % db_name)
            # Check osm2pgsql tool present
        options["osm2pgsql"] = search_path("osm2pgsql")
        if not options["osm2pgsql"]:
            raise CommandError("osm2pgsql not found. "\
                               "Install osm2pgsql and ensure "\
                               "it is in system $PATH")
            # Check --file or --bbox option is set
        if not options["file"] and not options["bbox"]:
            raise CommandError("Set either --file or --bbox")
            # Process
        if options["file"]:
            # Process existing file
            rbbox = self.process_file(options["file"], **options)
        else:
            # Download and process file
            # Check --bbox
            try:
                bbox = [float(b) for b in options["bbox"].split(",")]
            except ValueError, why:
                raise CommandError("Invalid bounding box format: %s" % why)
            if len(bbox) != 4:
                raise CommandError("Invalid bounding box format")
            if not ((-180 <= bbox[0] <= 180) and (-180 <= bbox[2] <= 180)):
                raise CommandError("Invalid bounding box:"\
                                   "Latitude must be between -180 and 180")
            if not ((-90 <= bbox[1] <= 90) and (-90 <= bbox[3] <= 90)):
                raise CommandError("Invalid bounding box:"\
                                   "Longiture must be between -90 and 90")
            bbox = [min(bbox[0], bbox[2]), min(bbox[1], bbox[3]),
                    max(bbox[0], bbox[2]), max(bbox[1], bbox[3])]
            # Download and process file
            with temporary_file() as p:
                print "Requesting OSM data"
                url = self.OSM_API_URL + ",".join([str(b) for b in bbox])
                print url
                u = urlopen(url)
                with open(p, "w") as f:
                    f.write(u.read())
                rbbox = self.process_file(p, **options)
        # Install new area
        if options["area"]:
            SW = [rbbox[0], rbbox[1]]
            NE = [rbbox[2], rbbox[3]]
            a = Area.objects.filter(name=options["area"]).first()
            if a:
                a.SW = SW
                a.NE = NE
                a.min_zoom = MIN_ZOOM
                a.max_zoom = MAX_ZOOM
            else:
                a = Area(
                    name=options["area"],
                    min_zoom=MIN_ZOOM,
                    max_zoom=MAX_ZOOM,
                    SW=SW,
                    NE=NE
                )
            a.save()
            print "Done"

    def process_file(self, path, osm2pgsql=None, **kwargs):
        """
        Upload OSM XML to database
        :returns: Bounding box
        :rtype: tuple
        """
        # Check file is exists
        if not os.access(path, os.R_OK):
            raise CommandError("Cannot read file '%s'" % path)
            # Run osm2pgsql
        args = [osm2pgsql, "-m", "-k", "-p", "gis_osm", "-G",
                "-S", "share/osm2pgsql/default.style",
                "-d", config.get("database", "name")]
        if config.get("database", "user"):
            args += ["-U", config.get("database", "user")]
        if config.get("database", "password"):
            args += ["-W"]  #, config.get("database", "password")]
        if config.get("database", "host"):
            args += ["-H", config.get("database", "host")]
        if config.get("database", "port"):
            args += ["-P", config.get("database", "port")]
        args += [path]
        print "Importing OSM data from file '%s'" % path
        subprocess.check_call(args)
        # Calculate and return bounding box
        with open(path) as f:
            d = f.read(4096)
        match = self.rx_bounds.search(d)
        if match:
            return parse_osm_bounds(match.group(1))
        match = self.rx_bound_box.search(d)
        if match:
            b = match.group(1).split(",")
            return tuple(float(x) for x in (b[1], b[0], b[3], b[2]))
        else:
            raise CommandError("Cannot find bounding box")
