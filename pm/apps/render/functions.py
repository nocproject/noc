# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Graphite-compatible functions
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from collections import defaultdict
import math
import datetime
import random
## Third-party modules
from graphite.attime import parseTimeOffset
## NOC modules
from data import TimeSeries, epoch
from noc.lib.dateutils import total_seconds
from graphite.glyph import format_units

NAN = float('NaN')
INF = float('inf')
## Function registry
functions = {}


def api(*names):
    """
    Decocator for functions definitions
    """
    def decorated(f):
        for name in names:
            functions[name] = f
        return f
    return decorated


##
## Utility functions
##
def format_path(series_list):
    """
    Returns a comma-separated list of unique path expressions.
    """
    pe = sorted(set([s.pathExpression for s in series_list]))
    return ",".join(pe)


def normalize(name, series_lists):
    sl = reduce(lambda x, y: x + y, series_lists)
    pe = "%s(%s)" % (name, format_path(sl))
    return pe, sl


def is_empty(series_lists):
    return not series_lists or series_lists == ([],)


def get_percentile(points, n, interpolate=False):
    """
    Percentile is calculated using the method outlined in the NIST Engineering
    Statistics Handbook:
    http://www.itl.nist.gov/div898/handbook/prc/section2/prc252.htm
    """
    sorted_points = sorted(p for p in points if p is not None)
    if len(sorted_points) == 0:
        return None
    fractional_rank = (n/100.0) * (len(sorted_points) + 1)
    rank = int(fractional_rank)
    rank_fraction = fractional_rank - rank

    if not interpolate:
        rank += int(math.ceil(rank_fraction))

    if rank == 0:
        percentile = sorted_points[0]
    elif rank - 1 == len(sorted_points):
        percentile = sorted_points[-1]
    else:
        percentile = sorted_points[rank - 1]  # Adjust for 0-index

    if interpolate:
        if rank != len(sorted_points):  # if a next value exists
            next_value = sorted_points[rank]
            percentile = percentile + rank_fraction * (next_value - percentile)

    return percentile


##
## API Functions (in alphabet order)
##
@api("absolute")
def absolute(ctx, series_list):
    """
    Takes one metric or a wildcard series_list and applies the mathematical abs
    function to each datapoint transforming it to its absolute value.

    Example::

        &target=absolute(Server.instance01.threads.busy)
        &target=absolute(Server.instance*.threads.busy)
    """
    for series in series_list:
        series.set_name("absolute(%s)" % series.name)
        series.apply(abs)
    return series_list


@api("alias")
def alias(ctx, series_list, new_name):
    """
    Takes one metric or a wildcard series_list and a string in quotes.
    Prints the string instead of the metric name in the legend.

    Example::

        &target=alias(Sales.widgets.largeBlue,"Large Blue Widgets")

    """
    try:
        series_list.set_name(new_name)
    except AttributeError:
        for series in series_list:
            series.set_name(new_name)
    return series_list


@api("alpha")
def alpha(ctx, series_list, alpha):
    """
    Assigns the given alpha transparency setting to the series. Takes a float
    value between 0 and 1.
    """
    for series in series_list:
        series.options['alpha'] = alpha
    return series_list


@api("averageAbove")
def averageAbove(ctx, series_list, n):
    """
    Takes one metric or a wildcard series_list followed by an integer N.
    Out of all metrics passed, draws only the metrics with an average value
    above N for the time period specified.

    Example::

        &target=averageAbove(server*.instance*.threads.busy,25)

    Draws the servers with average values above 25.

    """
    return [s for s in series_list if s.average() >= n]


@api("averageBelow")
def averageBelow(ctx, series_list, n):
    """
    Takes one metric or a wildcard series_list followed by an integer N.
    Out of all metrics passed, draws only the metrics with an average value
    below N for the time period specified.

    Example::

        &target=averageBelow(server*.instance*.threads.busy,25)

    Draws the servers with average values below 25.

    """
    return [s for s in series_list if s.average() <= n]


@api("avg", "averageSeries")
def averageSeries(ctx, *series_lists):
    """
    Short Alias: avg()

    Takes one metric or a wildcard series_list.
    Draws the average value of all metrics passed at each time.

    Example::

        &target=averageSeries(company.server.*.threads.busy)

    """
    def avg(p):
        if p:
            return sum(p) / len(p)
        else:
            return None

    if is_empty(series_lists):
        return []
    name, series_lists = normalize("averageSeries", series_lists)
    return [TimeSeries.fit_map(name, series_lists, avg, safe=True)]


@api("averageSeriesWithWildcards")
def averageSeriesWithWildcards(ctx, series_list, *positions):
    """
    Call averageSeries after inserting wildcards at the given position(s).

    Example::

        &target=averageSeriesWithWildcards(
            host.cpu-[0-7].cpu-{user,system}.value, 1)

    This would be the equivalent of::

        &target=averageSeries(host.*.cpu-user.value)&target=averageSeries(
            host.*.cpu-system.value)

    """
    matchedList = defaultdict(list)
    for series in series_list:
        newname = '.'.join(map(lambda x: x[1],
                               filter(lambda i: i[0] not in positions,
                                      enumerate(series.name.split('.')))))
        matchedList[newname].append(series)
    result = []
    for name in matchedList:
        [series] = averageSeries(ctx, (matchedList[name]))
        series.set_name(name)
        result.append(series)
    return result


@api("cactiStyle")
def cactiStyle(ctx, series_list, system=None):
    """
    Takes a series list and modifies the aliases to provide column aligned
    output with Current, Max, and Min values in the style of cacti. Optonally
    takes a "system" value to apply unit formatting in the same style as the
    Y-axis.
    NOTE: column alignment only works with monospace fonts such as terminus.

    Example::

        &target=cactiStyle(ganglia.*.net.bytes_out,"si")

    """
    if system:
        fmt = lambda x: "%.2f%s" % format_units(x, system=system)
    else:
        fmt = lambda x: "%.2f" % x
    l_name = max([0] + [len(series.name) for series in series_list])
    l_last = max([0] + [len(fmt(int(series.last() or 3)))
                         for series in series_list]) + 3
    max_len = max([0] + [len(fmt(int(series.max() or 3)))
                        for series in series_list]) + 3
    min_len = max([0] + [len(fmt(int(series.min() or 3)))
                        for series in series_list]) + 3
    for series in series_list:
        last = series.last()
        maximum = series.max()
        minimum = series.min()
        if last is None:
            last = NAN
        else:
            last = fmt(float(last))

        if maximum is None:
            maximum = NAN
        else:
            maximum = fmt(float(maximum))
        if minimum is None:
            minimum = NAN
        else:
            minimum = fmt(float(minimum))

        series.name = "%*s Current:%*s Max:%*s Min:%*s " % (
            -l_name, series.name, -l_last, last,
            -max_len, maximum, -min_len, minimum)
    return series_list


@api("color")
def color(ctx, series_list, color):
    """
    Assigns the given color to the series_list

    Example::

        &target=color(collectd.hostname.cpu.0.user, 'green')
        &target=color(collectd.hostname.cpu.0.system, 'ff0000')
        &target=color(collectd.hostname.cpu.0.idle, 'gray')
        &target=color(collectd.hostname.cpu.0.idle, '6464ffaa')

    """
    for series in series_list:
        series.color = color
    return series_list


@api("dashed")
def dashed(ctx, series_list, dash_length=5):
    """
    Takes one metric or a wildcard series_list, followed by a float F.

    Draw the selected metrics with a dotted line with segments of length F
    If omitted, the default length of the segments is 5.0

    Example::

        &target=dashed(server01.instance01.memory.free,2.5)

    """
    for series in series_list:
        series.set_name("dashed(%s, %d)" % (series.name, dash_length))
        series.options['dashed'] = dash_length
    return series_list


@api("countSeries")
def countSeries(ctx, *series_lists):
    """
    Draws a horizontal line representing the number of nodes found in the
    series_list.

    Example::

        &target=countSeries(carbon.agents.*.*)

    """
    def count(a):
        return int(len(a))

    if is_empty(series_lists):
        return []
    name, series_lists = normalize("countSeries", series_lists)
    return [TimeSeries.fit_map(name, series_lists, count, safe=True)]


@api("derivative")
def derivative(ctx, series_list):
    """
    This is the opposite of the integral function. This is useful for taking a
    running total metric and calculating the delta between subsequent data
    points.

    This function does not normalize for periods of time, as a true derivative
    would. Instead see the perSecond() function to calculate a rate of change
    over time.

    Example::

        &target=derivative(company.server.application01.ifconfig.TXPackets)

    Each time you run ifconfig, the RX and TXPackets are higher (assuming there
    is network traffic.) By applying the derivative function, you can get an
    idea of the packets per minute sent or received, even though you're only
    recording the total.
    """
    results = []
    for series in series_list:
        new_values = []
        prev = None
        for val, t in series:
            if None in (prev, val):
                new_values += [(None, t)]
                prev = val
                continue
            new_values += [(val - prev, t)]
            prev = val
        name = "derivative(%s)" % series.name
        results += [
            TimeSeries("derivative(%s)" % series.name,
                       series.start, series.end, new_values)
        ]
    return results


@api("diffSeries")
def diffSeries(ctx, *series_lists):
    """
    Can take two or more metrics.
    Subtracts parameters 2 through n from parameter 1.

    Example::

        &target=diffSeries(service.connections.total,
                           service.connections.failed)

    """
    def diff(values):
        return sum(
            [values[0] if values[0] is not None else 0] +
            [-v for v in values[1:] if v is not None]
        )

    if is_empty(series_lists):
        return []
    name, series_lists = normalize("diffSeries", series_lists)
    return [TimeSeries.fit_map(name, series_lists, diff)]


@api("drawAsInfinite")
def drawAsInfinite(ctx, series_list):
    """
    Takes one metric or a wildcard series_list.
    If the value is zero, draw the line at 0. If the value is above zero, draw
    the line at infinity. If the value is null or less than zero, do not draw
    the line.

    Useful for displaying on/off metrics, such as exit codes. (0 = success,
    anything else = failure.)

    Example::

        drawAsInfinite(Testing.script.exitCode)

    """
    for series in series_list:
        series.options["drawAsInfinite"] = True
        series.set_name("drawAsInfinite(%s)" % series.name)
    return series_list


@api("highestAverage")
def highestAverage(ctx, series_list, n=1):
    """
    Takes one metric or a wildcard series_list followed by an integer N.
    Out of all metrics passed, draws only the top N metrics with the highest
    average value for the time period specified.

    Example::

        &target=highestAverage(server*.instance*.threads.busy,5)

    Draws the top 5 servers with the highest average value.

    """
    return sorted(series_list, key=lambda s: s.average())[-n:]


@api("identity", "time", "timeFunction")
def identity(ctx, name):
    """
    Identity function:
    Returns datapoints where the value equals the timestamp of the datapoint.
    Useful when you have another series where the value is a timestamp, and
    you want to compare it to the time of the datapoint, to render an age

    Example::

        &target=identity("The.time.series")

    This would create a series named "The.time.series" that contains points
    where x(t) == t.
    """
    step = 60
    start = int(epoch(ctx["startTime"]))
    end = int(epoch(ctx["endTime"]))
    return [
        TimeSeries(
            "identity(%s)" % name,
            epoch(ctx["startTime"]),
            epoch(ctx["endTime"]),
            [(t, t) for t in range(start, end, step)]
        )
    ]


@api("integral")
def integral(ctx, series_list):
    """
    This will show the sum over time, sort of like a continuous addition
    function. Useful for finding totals or trends in metrics that are
    collected per minute.

    Example::

        &target=integral(company.sales.perMinute)

    This would start at zero on the left side of the graph, adding the sales
    each minute, and show the total sales for the time period selected at the
    right side, (time now, or the time specified by '&until=').
    """
    def integrate(v):
        current[0] += v
        return current[0]

    for series in series_list:
        current = [0.0]
        series.apply(integrate)
        series.set_name("integral(%s)" % series.name)
    return series_list


@api("isNonNull")
def isNonNull(ctx, series_list):
    """
    Takes a metric or wild card series_list and counts up how many
    non-null values are specified. This is useful for understanding
    which metrics have data at a given point in time (ie, to count
    which servers are alive).

    Example::

        &target=isNonNull(webapp.pages.*.views)

    Returns a series_list where 1 is specified for non-null values, and
    0 is specified for null values.
    """

    def indicator(v):
        if v is None:
            return 0
        else:
            return 1

    for series in series_list:
        series.apply(indicator, safe=False)
        series.set_name = "isNonNull(%s)" % series.name
    return series_list


@api("invert")
def invert(ctx, series_list):
    """
    Takes one metric or a wildcard series_list, and inverts each datapoint
    (i.e. 1/x).

    Example::

        &target=invert(Server.instance01.threads.busy)

    """
    for series in series_list:
        series.set_name("invert(%s)" % (series.name))
        series.apply(lambda x: 1 / x if x else None)
    return series_list


@api("lineWidth")
def lineWidth(ctx, series_list, width):
    """
    Takes one metric or a wildcard series_list, followed by a float F.

    Draw the selected metrics with a line width of F, overriding the default
    value of 1, or the &lineWidth=X.X parameter.

    Useful for highlighting a single metric out of many, or having multiple
    line widths in one graph.

    Example::

        &target=lineWidth(server01.instance01.memory.free,5)

    """
    for series in series_list:
        series.options['lineWidth'] = width
    return series_list


@api("limit")
def limit(ctx, series_list, n):
    """
    Takes one metric or a wildcard series_list followed by an integer N.

    Only draw the first N metrics. Useful when testing a wildcard in a
    metric.

    Example::

        &target=limit(server*.instance*.memory.free,5)

    Draws only the first 5 instance's memory free.

    """
    return series_list[0:n]


@api("log")
def logarithm(ctx, series_list, base=10):
    """
    Takes one metric or a wildcard series_list, a base, and draws the y-axis in
    logarithmic format. If base is omitted, the function defaults to base 10.

    Example::

        &target=log(carbon.agents.hostname.avgUpdateTime,2)

    """
    def l(v):
        if v <= 0:
            return None
        else:
            return math.log(v, base)

    base = int(base)
    for series in series_list:
        series.set_name("log(%s, %s)" % (series.name, base))
        series.apply(l)
    return series_list


@api("lowestAverage")
def lowestAverage(ctx, series_list, n=1):
    """
    Takes one metric or a wildcard series_list followed by an integer N.
    Out of all metrics passed, draws only the bottom N metrics with the lowest
    average value for the time period specified.

    Example::

        &target=lowestAverage(server*.instance*.threads.busy,5)

    Draws the bottom 5 servers with the lowest average value.

    """
    return sorted(series_list, key=lambda s: s.average())[:n]


@api("maximumAbove")
def maximumAbove(ctx, series_list, n):
    """
    Takes one metric or a wildcard series_list followed by a constant n.
    Draws only the metrics with a maximum value above n.

    Example::

        &target=maximumAbove(system.interface.eth*.packetsSent,1000)

    This would only display interfaces which at one point sent more than
    1000 packets/min.
    """
    return [s for s in series_list if s.max() > n]


@api("maximumBelow")
def maximumBelow(ctx, series_list, n):
    """
    Takes one metric or a wildcard series_list followed by a constant n.
    Draws only the metrics with a maximum value below n.

    Example::

        &target=maximumBelow(system.interface.eth*.packetsSent,1000)

    This would only display interfaces which always sent less than 1000
    packets/min.
    """
    return [s for s in series_list if s.max() <= n]


@api("maxSeries")
def maxSeries(ctx, *series_lists):
    """
    Takes one metric or a wildcard series_list. For each datapoint from each
    metric passed in, pick the maximum value and graph it.

    Example::

        &target=maxSeries(Server*.connections.total)

    """
    if is_empty(series_lists):
        return []
    name, series_lists = normalize("maxSeries", series_lists)
    return [TimeSeries.fit_map(name, series_lists, max, safe=True)]


@api("minumumAbove")
def minimumAbove(ctx, series_list, n):
    """
    Takes one metric or a wildcard series_list followed by a constant n.
    Draws only the metrics with a minimum value above n.

    Example::

        &target=minimumAbove(system.interface.eth*.packetsSent,1000)

    This would only display interfaces which always sent more than 1000
    packets/min.
    """
    return [s for s in series_list if s.min() > n]


@api("minimumBelow")
def minimumBelow(ctx, series_list, n):
    """
    Takes one metric or a wildcard series_list followed by a constant n.
    Draws only the metrics with a minimum value below n.

    Example::

        &target=minimumBelow(system.interface.eth*.packetsSent,1000)

    This would only display interfaces which sent at one point less than
    1000 packets/min.
    """
    return [s for s in series_list if s.min() <= n]


@api("minSeries")
def minSeries(ctx, *series_lists):
    """
    Takes one metric or a wildcard series_list.
    For each datapoint from each metric passed in, pick the minimum value and
    graph it.

    Example::

        &target=minSeries(Server*.connections.total)
    """
    if is_empty(series_lists):
        return []
    name, series_lists = normalize("minSeries", series_lists)
    return [TimeSeries.fit_map(name, series_lists, min, safe=True)]


@api("multiplySeries")
def multiplySeries(ctx, *series_lists):
    """
    Takes two or more series and multiplies their points. A constant may not be
    used. To multiply by a constant, use the scale() function.

    Example::

        &target=multiplySeries(Series.dividends,Series.divisors)


    """
    def mul(*factors):
        if None in factors:
            return None

        product = 1
        for factor in factors:
            product *= float(factor)
        return product

    if is_empty(series_lists):
        return []
    if len(series_lists) == 1:
        return series_lists
    name, series_lists = normalize("multiplySeries", series_lists)
    return [TimeSeries.fit_map(name, series_lists, mul, safe=True)]


@api("nonNegativeDerivative")
def nonNegativeDerivative(ctx, series_list, max_value=None):
    """
    Same as the derivative function above, but ignores datapoints that trend
    down. Useful for counters that increase for a long time, then wrap or
    reset. (Such as if a network interface is destroyed and recreated by
    unloading and re-loading a kernel module, common with USB / WiFi cards.

    Example::

        &target=nonNegativederivative(
            company.server.application01.ifconfig.TXPackets)

    """
    results = []

    for series in series_list:
        new_values = []
        prev = None
        for val, t in series:
            if None in (prev, val):
                new_values.append(None)
                prev = val
                continue
            diff = val - prev
            if diff >= 0:
                new_values.append(diff)
            elif max_value is not None and max_value >= val:
                new_values.append((max_value - prev) + val + 1)
            else:
                new_values.append(None)
            prev = val
        results += [
            TimeSeries("nonNegativeDerivative(%s)" % series.name,
                       series.start, series.end, new_values)
        ]
    return results


@api("offset")
def offset(ctx, series_list, factor):
    """
    Takes one metric or a wildcard series_list followed by a constant, and adds
    the constant to each datapoint.

    Example::

        &target=offset(Server.instance01.threads.busy,10)

    """
    factor = float(factor)
    for series in series_list:
        series.set_name("offset(%s,%g)" % (series.name, float(factor)))
        series.apply(lambda x: x + factor)
    return series_list


@api("offsetToZero")
def offsetToZero(ctx, series_list):
    """
    Offsets a metric or wildcard series_list by subtracting the minimum
    value in the series from each datapoint.

    Useful to compare different series where the values in each series
    may be higher or lower on average but you're only interested in the
    relative difference.

    An example use case is for comparing different round trip time
    results. When measuring RTT (like pinging a server), different
    devices may come back with consistently different results due to
    network latency which will be different depending on how many
    network hops between the probe and the device. To compare different
    devices in the same graph, the network latency to each has to be
    factored out of the results. This is a shortcut that takes the
    fastest response (lowest number in the series) and sets that to zero
    and then offsets all of the other datapoints in that series by that
    amount. This makes the assumption that the lowest response is the
    fastest the device can respond, of course the more datapoints that
    are in the series the more accurate this assumption is.

    Example::

        &target=offsetToZero(Server.instance01.responseTime)
        &target=offsetToZero(Server.instance*.responseTime)

    """
    for series in series_list:
        series.set_name("offsetToZero(%s)" % series.name)
        sm = series.min()
        for s in series_list:
            s.apply(lambda v: v - sm)
    return series_list


@api("percentileOfSeries")
def percentileOfSeries(ctx, series_lists, n, interpolate=False):
    """
    percentileOfSeries returns a single series which is composed of the
    n-percentile values taken across a wildcard series at each point.
    Unless `interpolate` is set to True, percentile values are actual values
    contained in one of the supplied series.
    """
    if n <= 0:
        raise ValueError(
            'The requested percent is required to be greater than 0')

    if not series_lists:
        return []
    _, series_lists = normalize("percentileOfSeries", series_lists)
    name = "percentileOfSeries(%s,%g)" % (series_lists[0].pathExpression, n)
    return [
        TimeSeries.fit_map(
            name, series_lists,
            lambda x: get_percentile(x, n, interpolate),
            safe=True
        )
    ]


@api("randomWalk", "randomWalkFunction")
def randomWalkFunction(ctx, name):
    """
    Short Alias: randomWalk()

    Returns a random walk starting at 0. This is great for testing when there
    is no real data in whisper.

    Example::

        &target=randomWalk("The.time.series")

    This would create a series named "The.time.series" that contains points
    where x(t) == x(t-1)+random()-0.5, and x(0) == 0.
    """
    step = 60
    delta = datetime.timedelta(seconds=step)
    when = ctx["startTime"]
    values = []
    current = 0
    while when < ctx["endTime"]:
        t = epoch(when)
        values += [(current, t)]
        current += random.random() - 0.5
        when += delta
    return [
        TimeSeries(
            "randomWalk(%s)" % name,
            epoch(ctx["startTime"]),
            epoch(ctx["endTime"]),
            values
        )
    ]


@api("rangeOfSeries")
def rangeOfSeries(ctx, *series_lists):
    """
    Takes a wildcard series_list.
    Distills down a set of inputs into the range of the series

    Example::

        &target=rangeOfSeries(Server*.connections.total)

    """
    def rng(a):
        min_a = min(a)
        max_a = max(a)
        if min_a is None or max_a is None:
            return None
        else:
            return max_a - min_a

    if is_empty(series_lists):
        return []
    name, series_lists = normalize("rangeOfSeries", series_lists)
    return [TimeSeries.fit_map(name, series_lists, rng, safe=True)]


@api("secondYAxis")
def secondYAxis(ctx, series_list):
    """
    Graph the series on the secondary Y axis.
    """
    for series in series_list:
        series.options["secondYAxis"] = True
        series.set_name("secondYAxis(%s)" % series.name)
    return series_list


@api("scale")
def scale(ctx, series_list, factor):
    """
    Takes one metric or a wildcard series_list followed by a constant, and
    multiplies the datapoint by the constant provided at each point.

    Example::

        &target=scale(Server.instance01.threads.busy,10)
        &target=scale(Server.instance*.threads.busy,10)

    """
    factor = float(factor)
    for series in series_list:
        series.set_name("scale(%s,%g)" % (series.name, float(factor)))
        series.apply(lambda x: x * factor)
    return series_list


@api("sin", "sinFunction")
def sinFunction(ctx, name, amplitude=1):
    """
    Short Alias: sin()

    Just returns the sine of the current time. The optional amplitude parameter
    changes the amplitude of the wave.

    Example::

        &target=sin("The.time.series", 2)

    This would create a series named "The.time.series" that contains sin(x)*2.
    """
    step = 60
    delta = datetime.timedelta(seconds=step)
    when = ctx["startTime"]
    values = []
    while when < ctx["endTime"]:
        t = epoch(when)
        values += [(math.sin(t) * amplitude, t)]
        when += delta
    return [
        TimeSeries(
            "sin(%s)" % name,
            epoch(ctx["startTime"]),
            epoch(ctx["endTime"]),
            values
        )
    ]


@api("stddevSeries")
def stddevSeries(ctx, *series_lists):
    """

    Takes one metric or a wildcard series_list.
    Draws the standard deviation of all metrics passed at each time.

    Example::

        &target=stddevSeries(company.server.*.threads.busy)

    """
    def stddev(a):
        sm = sum(a)
        ln = len(a)
        avg = sm / ln
        s = 0
        for v in a:
            s += (v - avg) ** 2
        return math.sqrt(s / ln)

    if is_empty(series_lists):
        return []
    name, series_lists = normalize("stddevSeries", series_lists)
    return [TimeSeries.fit_map(name, series_lists, stddev, safe=True)]


@api("sum", "sumSeries")
def sumSeries(ctx, *series_lists):
    """
    Short form: sum()

    This will add metrics together and return the sum at each datapoint. (See
    integral for a sum over time)

    Example::

        &target=sum(company.server.application*.requestsHandled)

    This would show the sum of all requests handled per minute (provided
    requestsHandled are collected once a minute).     If metrics with different
    retention rates are combined, the coarsest metric is graphed, and the sum
    of the other metrics is averaged for the metrics with finer retention
    rates.

    """
    if is_empty(series_lists):
        return []
    name, series_lists = normalize("sumSeries", series_lists)
    return [TimeSeries.fit_map(name, series_lists, sum, safe=True)]


@api("time_shift")
def time_shift(ctx, series_list, time_shift, reset_end=True):
    """
    Takes one metric or a wildcard series_list, followed by a quoted string
    with the length of time (See ``from / until`` in the render\_api_ for
    examples of time formats).

    Draws the selected metrics shifted in time. If no sign is given, a minus
    sign ( - ) is implied which will shift the metric back in time. If a plus
    sign ( + ) is given, the metric will be shifted forward in time.

    Will reset the end date range automatically to the end of the base stat
    unless reset_end is False. Example case is when you timeshift to last week
    and have the graph date range set to include a time in the future, will
    limit this timeshift to pretend ending at the current time. If reset_end is
    False, will instead draw full range including future time.

    Useful for comparing a metric against itself at a past periods or
    correcting data stored at an offset.

    Example::

        &target=time_shift(Sales.widgets.largeBlue,"7d")
        &target=time_shift(Sales.widgets.largeBlue,"-7d")
        &target=time_shift(Sales.widgets.largeBlue,"+1h")

    """
    from graphite.evaluator import evaluateTarget

    if not series_list:
        return []
    # Default to negative. parseTimeOffset defaults to +
    if time_shift[0].isdigit():
        time_shift = '-' + time_shift
    delta = parseTimeOffset(time_shift)
    new_ctx = ctx.copy()
    new_ctx['startTime'] = ctx['startTime'] + delta
    new_ctx['endTime'] = ctx['endTime'] + delta
    results = []
    # if len(series_list) > 1, they will all have the same pathExpression,
    # which is all we care about.
    series = series_list[0]
    for shifted_series in evaluateTarget(new_ctx, series.pathExpression):
        shifted_series.set_name('time_shift(%s, %s)' % (
            shifted_series.name, time_shift))
        if reset_end:
            shifted_series.end = series.end
        else:
            shifted_series.end = (
                shifted_series.end - shifted_series.start + series.start)
        shifted_series.start = series.start
        results += [shifted_series]
    return results


@api("sumSeriesWithWildcards")
def sumSeriesWithWildcards(ctx, series_list, *positions):
    """
    Call sumSeries after inserting wildcards at the given position(s).

    Example::

        &target=sumSeriesWithWildcards(host.cpu-[0-7].cpu-{user,system}.value,
                                       1)

    This would be the equivalent of::

        &target=sumSeries(host.*.cpu-user.value)&target=sumSeries(
            host.*.cpu-system.value)

    """
    newSeries = {}
    new_names = list()

    for series in series_list:
        newname = '.'.join(map(lambda x: x[1],
                               filter(lambda i: i[0] not in positions,
                                      enumerate(series.name.split('.')))))
        if newname in newSeries:
            newSeries[newname] = sumSeries(ctx,
                                           (series, newSeries[newname]))[0]
        else:
            newSeries[newname] = series
            new_names.append(newname)
        newSeries[newname].name = newname

    return [newSeries[name] for name in new_names]


@api("transformNull")
def transformNull(ctx, series_list, default=0):
    """
    Takes a metric or wild card series_list and an optional value
    to transform Nulls to. Default is 0. This method compliments
    drawNullAsZero flag in graphical mode but also works in text only
    mode.

    Example::

        &target=transformNull(webapp.pages.*.views,-1)

    This would take any page that didn't have values and supply negative 1 as
    a default. Any other numeric value may be used as well.
    """
    def transform(v):
        if v is None:
            return default
        else:
            return v

    for series in series_list:
        series.apply(transform, safe=False)
        series.set_name("transformNull(%s,%g)" % (series.name, default))
    return series_list

## Graphite functions to be ported frim graphite/functions
## Remove appropriative lines for ported functions
#     # Combine functions
#     'weightedAverage': weightedAverage,
#     # Transform functions
#     'scaleToSeconds': scaleToSeconds,
#     'perSecond': perSecond,
#     'timeStack': timeStack,
#     'summarize': summarize,
#     'smartSummarize': smartSummarize,
#     'hitcount': hitcount,
#     # Calculate functions
#     'movingAverage': movingAverage,
#     'movingMedian': movingMedian,
#     'stdev': stdev,
#     'holtWintersForecast': holtWintersForecast,
#     'holtWintersConfidenceBands': holtWintersConfidenceBands,
#     'holtWintersConfidenceArea': holtWintersConfidenceArea,
#     'holtWintersAberration': holtWintersAberration,
#     'asPercent': asPercent,
#     'pct': asPercent,
#     'diffSeries': diffSeries,
#     'divideSeries': divideSeries,
#     # Series Filter functions
#     'mostDeviant': mostDeviant,
#     'highestCurrent': highestCurrent,
#     'lowestCurrent': lowestCurrent,
#     'highestMax': highestMax,
#     'currentAbove': currentAbove,
#     'currentBelow': currentBelow,
#     'nPercentile': nPercentile,
#     'sortByTotal': sortByTotal,
#     'sortByName': sortByName,
#     'averageOutsidePercentile': averageOutsidePercentile,
#     'removeBetweenPercentile': removeBetweenPercentile,
#     'sortByMaxima': sortByMaxima,
#     'sortByMinima': sortByMinima,
#     'useSeriesAbove': useSeriesAbove,
#     'exclude': exclude,
#     # Data Filter functions
#     'removeAbovePercentile': removeAbovePercentile,
#     'removeAboveValue': removeAboveValue,
#     'removeBelowPercentile': removeBelowPercentile,
#     'removeBelowValue': removeBelowValue,
#     # Special functions
#     'legendValue': legendValue,
#     'aliasSub': aliasSub,
#     'aliasByNode': aliasByNode,
#     'aliasByMetric': aliasByMetric,
#     'cumulative': cumulative,
#     'consolidateBy': consolidateBy,
#     'keepLastValue': keepLastValue,
#     'changed': changed,
#     'secondYAxis': secondYAxis,
#     'substr': substr,
#     'group': group,
#     'map': mapSeries,
#     'reduce': reduceSeries,
#     'groupByNode': groupByNode,
#     'constantLine': constantLine,
#     'stacked': stacked,
#     'areaBetween': areaBetween,
#     'threshold': threshold,
#     'aggregateLine': aggregateLine
