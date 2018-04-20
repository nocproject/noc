.. _apps_main_timepattern:

Time Patterns
*************
Time patterns are the flexible way to identify time intervals. Time Pattern *matches* time interval
when it returns True for every moment of time belonging to interval and returns False for every other moment.

Time Patterns contains zero or more Terms. Zero-term Time Pattern matches any time.
One-term Time Pattern matches time interval defined by Term. Many-term Time Pattern
matches all intervals defined by Terms (Logical OR).

Each term contains mandatory left part and arbitrary right, separated by pipe sign (|).
Left part defines *Date Selector* while right part defines *Time Selector*. Term matches
moment of time when *Date Selector* matches *Date* and *Time Selector* matches *Time*.

Date and time selectors contains of zero or more expresions, separated by commas (,).
Empty expression matches any date or time. Multiple expressions match moment of time when
at least one expression matches.

Date Selector Expressions
-------------------------

=============================================== ===========================================================================
<day>                                           Matches day of month <day> of every month
<day1>-<day2>                                   Matches all days of month between <day1> and <day2> of every month
<day>.<month>                                   Matches date
<day1>.<month1>-<day2>.<month2>                 Matches all days between two dates of every year
<day>.<month>.<year>                            Matches date
<day1>.<month1>.<year1>-<day2>.<month2>.<year2> Matches all days between two dates
<day of week>                                   Matches day of week of every week (mon, tue, wen, thu, fri, sat, sun)
<day of week1>-<day of week2>                   Matches all days between two days of week
=============================================== ===========================================================================

Time Selector
-------------

=========== ==========================
HH:MM       Matches time
HH:MM-HH:MM Matches interval of time
=========== ==========================

Examples
--------

Any time::

    <empty rule>

Every 5th of month::

    05

From 5th to 10th of month::

    05-10

13th of March::

    13.03

From 1st of May to 7th of June::

    01.05-07.06
    
Each Friday::

    fri

From Monday to Friday::

    mon-fri

5th and 25th of every month::

    05,25

Working time (09:00-18:00 from Monday to Friday)::

    mon-fri|09:00-18:00

Non working time (All other time)::
    
    mon-fri|00:00-08:59,18:01-23:59
    sat,sun

Before noon of Monday, Wednesday and Friday, after noon for other days::

    mon,wen,fri|00:00-11:59
    tue,thu,sat,sun|12:00-23:59
