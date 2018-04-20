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
## Django modules
from django.core.cache import cache
from django.http import HttpResponse
## Third-party modules
import pytz
try:
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.lineplots import LinePlot
    from reportlab.graphics.charts.legends import LineLegend
    from reportlab.lib.colors import Color
except ImportError:
    pass
## NOC modules
from noc.lib.app import ExtApplication, view
from noc.sa.interfaces.base import (StringParameter, IntParameter,
                                    ListOfParameter)
from settings import config, TIME_ZONE
from noc.lib.serialize import json_encode
from data import TimeSeries
from noc.lib.colors import get_float_pallete
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

    # Empty space around the borders of chart
    X_PADDING = 10
    Y_PADDING = 10
    #

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
              "maxDataPoints": IntParameter(required=False)
          },
          api=True)
    def api_render(self, request,
                   graphType=None, pieMode=None, cacheTimeout=None,
                   target=None, localOnly=None, tz=None, pickle=None,
                   rawData=None, jsonp=None,
                   noCache=None, format=None,
                   maxDataPoints=None,
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
        try:
            t0 = parseATTime(kwargs.get("from", "-1d"))
            t1 = parseATTime(kwargs.get("until", "now"))
        except Exception, why:
            return self.response_bad_request(
                "Cannot parse time: %s" % why
            )
        if t0 == t1:
            return self.response_bad_request("Empty time range")
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
        use_cache = not request_opts["noCache"]
        cache_timeout = request_opts["cacheTimeout"]
        ctx = {
            "startTime": request_opts["startTime"],
            "endTime": request_opts["endTime"],
            "localOnly": request_opts["localOnly"],
            "maxDataPoints": maxDataPoints,
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
                    if not t.strip():
                        continue
                    data.extend(evaluateTarget(ctx, t))
                if use_cache:
                    cache.set(
                        data_key,
                        [d.get_info() for d in data],
                        cache_timeout
                    )
            else:
                # Convert cached data to Time Series
                data = [TimeSeries(**a) for a in cached_data]
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

    def get_raw_response(self, data, opts):
        response = HttpResponse(mimetype="text/plain")
        for series in data:
            response.write(
                "%s,%d,%d,%d|%s\n" % (
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
            r += [{"target": series.name, "datapoints": list(series)}]
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

    def get_pickle_response(self, data, opts):
        response = HttpResponse(mimetype="application/pickle")
        info = [series.getInfo() for series in data]
        pickle.dump(info, response, protocol=-1)
        return response

    def render_graph(self, request_opts, graph_opts):
        def label_fmt(x):
            print "@@@", x
            return str(x)

        ld = len(graph_opts["data"])
        palette = [Color(*x) for x in get_float_pallete(ld)]
        w = graph_opts["width"]
        h = graph_opts["height"]
        drawing = Drawing(w, h)
        # Legend
        legend = LineLegend()
        legend.colorNamePairs = [
            (palette[i], graph_opts["data"][i].name)
            for i in range(ld)
        ]
        legend.boxAnchor = "sw"
        legend.columnMaximum = 2
        legend.alignment = "right"
        drawing.add(legend)
        lh = legend._calcHeight() + self.X_PADDING / 2
        # Plot
        lp = LinePlot()
        lfs = lp.xValueAxis.labels.fontSize
        lp.x = self.X_PADDING
        lp.y = self.Y_PADDING + lh + lfs
        lp.width = w - 2 * self.X_PADDING
        lp.height = h - self.Y_PADDING - lp.y
        lp.data = [
            [(t, v) for v, t in ts] for ts in graph_opts["data"]
        ]
        for i in range(ld):
            lp.lines[i].strokeColor = palette[i]
        drawing.add(lp)
        # Render
        cdata = drawing.asString(format="png")
        response = self.render_plain_text(
            cdata,
            mimetype="image/png"
        )
        if not request_opts["noCache"]:
            cache.set(request_opts["requestKey"], response,
                      request_opts["cacheTimeout"])
        return response
