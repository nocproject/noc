# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## TileCache updater
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import logging
import threading
import Queue
import time
import datetime
## NOC modules
from noc.settings import config, IS_TEST
from noc.gis.models import TileCache, Area
from noc.gis.mapxml import map_to_xml
from noc.gis.geo import xy_to_ll, ll_to_xy, TS, MIN_ZOOM, MAX_ZOOM
## Third-party modules
try:
    import mapnik2
except ImportError, why:
    if not IS_TEST:
        raise ImportError(*why)


# Render additional N tiles around areas
PAD_TILES = config.getint("gis", "tilecache_padding")


class TileWorker(object):
    def __init__(self, map, instance, queue, xml):
        self.map = map
        self.label = "%s::%d" % (map.name, instance)
        self.queue = queue
        self.log("Running TileWorker")
        self.xml = xml

    def render_tile(self, zoom, x, y):
        t0 = time.time()
        tl = "(zoom=%s x=%s y=%s)" % (zoom, x, y)
        self.log("Rendering tile %s" % tl)
        # Convert tile index to LatLong (EPSG:4326)
        l0 = xy_to_ll(zoom, (x, y + 1))
        l1 = xy_to_ll(zoom, (x + 1, y))
        # Convert to map projection (e.g. mercator co-ords EPSG:900913)
        # and get tile's bounding box
        c0 = self.prj.forward(mapnik2.Coord(l0[0], l0[1]))
        c1 = self.prj.forward(mapnik2.Coord(l1[0], l1[1]))
        bbox = mapnik2.Box2d(c0.x, c0.y, c1.x, c1.y)
        # Render
        self.m.resize(TS, TS)
        self.m.zoom_to_box(bbox)
        self.m.buffer_size = 128
        im = mapnik2.Image(TS, TS)
        mapnik2.render(self.m, im)
        data = im.tostring("png256")
        # Save to database
        tc = TileCache.objects.filter(map=self.map.id,
                                      zoom=zoom, x=x, y=y).first()
        if tc:
            tc.ready = True
            tc.last_updated = datetime.datetime.now()
            tc.data = data
            tc.save()
        else:
            TileCache(
                map=self.map.id,
                zoom=zoom,
                x=x,
                y=y,
                ready=True,
                last_updated=datetime.datetime.now(),
                data=data).save()
        self.log("Tile %s completed in %dms" % (tl, (time.time() - t0) * 1000))

    def log(self, msg):
        logging.info("[%s]: %s" % (self.label, msg))

    def run(self):
        self.log("Loading map XML")
        self.m = mapnik2.Map(TS, TS)
        try:
            mapnik2.load_map_from_string(self.m, self.xml)
        except RuntimeError, why:
            logging.error("Cannot load map: %s" % why)
            os._exit(1)
        self.prj = mapnik2.Projection(self.m.srs)
        self.log("Waiting for tasks")
        while True:
            t = self.queue.get()
            if t is None:
                self.log("Stopping")
                self.queue.task_done()
                break
            zoom, x, y = t
            self.render_tile(zoom, x, y)
            self.queue.task_done()
        self.log("Stopped")


class TileTask(object):
    def __init__(self, map, nworkers=4, force=False):
        self.map = map
        self.nworkers = nworkers
        self.label = "[TileCache::%s]" % self.map.name
        self.force = force

    def log(self, msg):
        logging.info("%s %s" % (self.label, msg))

    def gen_tasks(self):
        """
        Generator returning a tiles coordinates to render

        @todo: Replace naive implementation with collision detection
        :return: (zoom, x, y)
        """
        for zoom in range(MIN_ZOOM, MAX_ZOOM + 1):
            seen = set()  # (x, y)
            M = 2 ** zoom - 1
            # Find all areas suitable for zoom
            for area in Area.objects.filter(is_active=True,
                                            min_zoom__lte=zoom,
                                            max_zoom__gte=zoom):
                # Get area tiles
                SW = ll_to_xy(zoom, area.SW)
                NE = ll_to_xy(zoom, area.NE)
                left = max(SW[0] - PAD_TILES, 0)
                right = min(NE[0] + PAD_TILES, M)
                top = max(NE[1] - PAD_TILES, 0)
                bottom = min(SW[1] + PAD_TILES, M)
                a_size = (right - left + 1) * (bottom - top + 1)
                self.log("Checking area '%s' at zoom level %d "\
                         " (%d x %d = %d tiles)" % (area.name, zoom,
                                                    right - left + 1,
                                                    bottom - top + 1,
                                                    a_size))
                seen |= set((tc.x, tc.y) for tc in TileCache.objects.filter(
                    map=self.map.id, zoom=zoom).only("x", "y"))
                for x in range(left, right + 1):
                    for y in range(top, bottom + 1):
                        c = (x, y)
                        if c in seen:
                            continue
                        seen.add(c)
                        if not self.force:
                            # Check tile is ready
                            tc = TileCache.objects.filter(map=self.map.id,
                                                          zoom=zoom, x=x,
                                                          y=y).first()
                            if tc and tc.ready:
                                continue
                        yield (zoom, x, y)

    def run(self):
        t0 = time.time()
        # Look for active areas
        self.log("Looking for areas:")
        n = 0
        for a in Area.objects.order_by("name"):
            self.log("    %s [%s - %s] %s Zoom %d - %d" %(
                a.name, a.SW, a.NE,
                "(active)" if a.is_active else "(disabled)",
                a.min_zoom, a.max_zoom
            ))
            if a.is_active:
                n += 1
        if n:
            self.log("%d active areas found" % n)
        else:
            self.log("No active areas found. Exiting")
            return
        #
        self.log("Processing map '%s'" % self.map.name)
        self.log("Preparing map.xml")
        xml = str(map_to_xml(self.map))
        # Initializing workers
        self.log("Initializing %d workers" % self.nworkers)
        queue = Queue.Queue(self.nworkers * 2)
        workers = []
        for i in range(self.nworkers):
            w = TileWorker(self.map, i, queue, xml)
            workers += [threading.Thread(target=w.run)]
        self.log("Starting workers")
        # Starting workers
        for w in workers:
            w.start()
        # Feeding workers
        self.log("Sending tasks")
        nt = 0
        for t in self.gen_tasks():
            queue.put(t)
            nt += 1
        # Stopping workers
        self.log("Waiting for workers")
        queue.join()
        # Sending stop signal to workers
        self.log("Stopping workers")
        for i in range(self.nworkers):
            queue.put(None)
        # Waiting for workers
        for w in workers:
            w.join()
        dt = time.time() - t0
        speed = float(nt) / dt if nt and dt > 0 else 0
        self.log("Finishing processing map '%s'. " \
                 "%d tiles processed in %8.2fs (%8.2f tiles/s)" % (
            self.map.name, nt, dt, speed))
