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
## NOC modules
from data import TimeSeries, epoch

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
        series.name = name
        result.append(series)
    return result


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
# SeriesFunctions = {
#     # Combine functions
#     'weightedAverage': weightedAverage,
#
#     # Transform functions
#     'scaleToSeconds': scaleToSeconds,
#     'offsetToZero': offsetToZero,
#     'perSecond': perSecond,
#     'integral': integral,
#     'timeStack': timeStack,
#     'timeShift': timeShift,
#     'summarize': summarize,
#     'smartSummarize': smartSummarize,
#     'hitcount': hitcount,
#
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
#
#     # Series Filter functions
#     'mostDeviant': mostDeviant,
#     'highestCurrent': highestCurrent,
#     'lowestCurrent': lowestCurrent,
#     'highestMax': highestMax,
#     'currentAbove': currentAbove,
#     'currentBelow': currentBelow,
#     'highestAverage': highestAverage,
#     'lowestAverage': lowestAverage,
#     'nPercentile': nPercentile,
#     'sortByTotal': sortByTotal,
#     'sortByName': sortByName,
#     'averageOutsidePercentile': averageOutsidePercentile,
#     'removeBetweenPercentile': removeBetweenPercentile,
#     'sortByMaxima': sortByMaxima,
#     'sortByMinima': sortByMinima,
#     'useSeriesAbove': useSeriesAbove,
#     'exclude': exclude,
#
#     # Data Filter functions
#     'removeAbovePercentile': removeAbovePercentile,
#     'removeAboveValue': removeAboveValue,
#     'removeBelowPercentile': removeBelowPercentile,
#     'removeBelowValue': removeBelowValue,
#
#     # Special functions
#     'legendValue': legendValue,
#     'aliasSub': aliasSub,
#     'aliasByNode': aliasByNode,
#     'aliasByMetric': aliasByMetric,
#     'cactiStyle': cactiStyle,
#     'cumulative': cumulative,
#     'consolidateBy': consolidateBy,
#     'keepLastValue': keepLastValue,
#     'changed': changed,
#     'drawAsInfinite': drawAsInfinite,
#     'secondYAxis': secondYAxis,
#     'lineWidth': lineWidth,
#     'dashed': dashed,
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
