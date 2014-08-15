# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## pm.render application
## Port of graphite-web renderer to NOC platform
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import time
import csv
import datetime
import cPickle as pickle
from cStringIO import StringIO
## Django modules
from django.core.cache import cache
from django.http import HttpResponse
## Third-party modules
import pytz
## NOC modules
from noc.lib.app import ExtApplication, view
from noc.sa.interfaces.base import (StringParameter, IntParameter,
                                    ListOfParameter)
from settings import config, TIME_ZONE
from noc.lib.serialize import json_encode
## Graphite contribution
from graphite.glyph import GraphTypes
from graphite.attime import parseATTime
from graphite.hashing import hashRequest, hashData
from graphite.evaluator import evaluateTarget
from graphite.functions import PieFunctions


class RenderApplication(ExtApplication):
    """
    Graphite-compatible render
    """
    title = "Render"

    DEFAULT_GRAPH_WIDTH = 330
    DEFAULT_GRAPH_HEIGTH = 250

    @view(url="^$", method=["GET"], access="launch",
          validate={
              "graphType": StringParameter(
                  default="line",
                  choices=GraphTypes.keys()
              ),
              "pieMode": StringParameter(
                  default="average",
                  # @todo: Specify all modes
                  choices=["average"]
              ),
              "cacheTimeout": IntParameter(
                  min_value=0,
                  default=config.getint("pm_render", "cache_duration")
              ),
              "target": ListOfParameter(
                  element=StringParameter(),
                  convert=True, default=[]
              ),
              "localOnly": StringParameter(default="0"),
              "tz": StringParameter(default=TIME_ZONE),
              "pickle": StringParameter(required=False),
              "rawData": StringParameter(required=False),
              "jsonp": StringParameter(required=False),
              "format": StringParameter(required=False),
              "noCache": StringParameter(required=False),
          },
          api=True)
    def api_render(self, request,
                   graphType=None, pieMode=None, cacheTimeout=None,
                   target=None, localOnly=None, tz=None, pickle=None,
                   rawData=None, jsonp=None,
                   noCache=None, format=None,
                   **kwargs):
        # Get timezone info
        try:
            tz = pytz.timezone(tz)
        except pytz.UnknownTimeZoneError:
            tz = pytz.timezone(TIME_ZONE)
        # Get format
        if pickle is not None:
            format = "pickle"
        elif rawData is not None:
            format = "raw"
        # Get time range
        t0 = parseATTime(kwargs.get("from", "-1d"))
        t1 = parseATTime(kwargs.get("until", "now"))
        assert t0 != t1, "Empty time range"
        # Collect parameters
        request_opts = {
            "graphType": graphType,
            "graphClass": GraphTypes[graphType],
            "pieMode": pieMode,
            "targets": target or [],
            "localOnly": localOnly == "1",
            "tzinfo": tz,
            "format": format,
            "noCache": noCache is not None,
            "startTime": min(t0, t1),
            "endTime": max(t0, t1),
            "cacheTimeout": cacheTimeout
        }
        if format:
            request_opts["format"] = format
            if jsonp is not None:
                request_opts["jsonp"] = jsonp
        # Fill possible graph options
        graph_opts = {
            "width": self.DEFAULT_GRAPH_WIDTH,
            "height": self.DEFAULT_GRAPH_HEIGTH,
        }
        if format == "svg":
            graph_opts["outputFormat"] = "svg"
        for opt in request_opts["graphClass"].customizable:
            if opt in kwargs:
                v = kwargs[opt]
                if opt not in ("fgcolor", "bgcolor", "fontColor"):
                    try:
                        graph_opts[opt] = int(v)
                        continue
                    except ValueError:
                        pass
                try:
                    graph_opts[opt] = float(v)
                    continue
                except ValueError:
                    pass
                if v.lower() in ("true", "false"):
                    graph_opts[opt] = v.lower() == "true"
                    continue
                if not v or v.lower() == "default":
                    continue
                graph_opts[opt] = v
        start = time.time()
        use_cache = not request_opts["noCache"]
        cache_timeout = request_opts["cacheTimeout"]
        ctx = {
            "startTime": request_opts["startTime"],
            "endTime": request_opts["endTime"],
            "localOnly": request_opts["localOnly"],
            "data": []
        }
        data = ctx["data"]
        # Try to use cached response
        if use_cache:
            request_key = hashRequest(request)
            cached_response = cache.get(request_key)
            if cached_response:
                return cached_response
            else:
                request_opts["requestKey"] = request_key
        # Cache miss, prepare requested data
        if graphType == "pie":
            for t in request_opts["targets"]:
                if ":" in t:
                    try:
                        name, value = t.split(":", 1)
                        data += [(name, float(value))]
                    except ValueError:
                        raise ValueError("Invalid target: '%s'" % t)
                else:
                    for series in evaluateTarget(ctx, t):
                        f = PieFunctions(request_opts["pieMode"])
                        data += [(series.name, f(ctx, series) or 0)]
        elif graphType == "line":
            if use_cache:
                # Store cached data
                data_key = hashData(request_opts["targets"],
                                    request_opts["startTime"],
                                    request_opts["endTime"])
                cached_data = cache.get(data_key)
            else:
                cached_data = None
            if cached_data is None:
                for t in request_opts["targets"]:
                    data.extend(evaluateTarget(ctx, t))
                if use_cache:
                    cache.set(data_key, data, cache_timeout)
        # Return data in requested format
        h = getattr(self, "get_%s_response" % request_opts["format"], None)
        if h:
            r = h(data, request_opts)
        else:
            graph_opts["data"] = data
            r = self.render_graph(request_opts, graph_opts)
        r["Pragma"] = "no-cache"
        r["Cache-Control"] = "no-cache"
        return r

    def get_raw_reponse(self, data, opts):
        response = HttpResponse(mimetype="text/plain")
        for series in data:
            response.write(
                "%s,%d,%d.%d|%s\n" % (
                    series.name, series.start, series.end, series.step,
                    ",".join(str(x) for x in series))
            )
        return response

    def get_csv_response(self, data, opts):
        response = HttpResponse(mimetype="text/csv")
        writer = csv.writer(response, dialect="excel")
        for series in data:
            for i, value in enumerate(series):
                ts = datetime.datetime.fromtimestamp(
                    series.start + i * series.step, opts["tzinfo"])
                writer.writerow([
                    series.name,
                    ts.strftime("%Y-%m-%d %H:%M:%S"),
                    value
                ])
        return response

    def get_json_response(self, data, opts):
        r = []
        for series in data:
            timestamps = range(series.start, series.end, series.step)
            datapoints = zip(series, timestamps)
            r += [{"target": series.name, "datapoints": datapoints}]
        c = json_encode(r)
        if opts.get("jsonp"):
            return HttpResponse(
                mimetype="text/javascript",
                content="%s(%s)" % (opts["jsonp"], c)
            )
        else:
            return HttpResponse(
                mimetype="application/json",
                content=c
            )

    def get_pickle(self, data, opts):
        response = HttpResponse(mimetype="application/pickle")
        info = [series.getInfo() for series in data]
        pickle.dump(info, response, protocol=-1)
        return response

    def render_graph(self, request_opts, graph_opts):
        # Render PNG
        out = StringIO()
        img = request_opts["graphClass"](**graph_opts)
        img.output(out)
        img_data = out.getvalue()
        out.close()
        #
        use_svg = graph_opts.get("outputFormat") == "svg"
        if use_svg and request_opts.get("jsonp") is not None:
            response = HttpResponse(
                content="%s(%s)" % (
                    request_opts["jsonp"], json_encode(img_data)),
                mimetype='text/javascript')
        else:
            response = HttpResponse(
                content=img_data,
                mimetype="image/svg+xml" if use_svg else "image/png"
            )
        if not request_opts["noCache"]:
            cache.set(request_opts["requestKey"], response,
                      request_opts["cacheTimeout"])
        return response
