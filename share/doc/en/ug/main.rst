****
Main
****
Overview
========
Main module is a core or noc. Main module provides following services:

* Core system services
* Database access, migration and backup tools
* User authentication and authorization
* Online documentation access
* Global search
* Reporting engine

Concepts
=========

Time Patterns
=============
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

Notification Groups
===================
Notification Groups are the unified method to deliver the message to all participants. Messages can be delivered
via email, written to file, etc. Messages are delivered by *noc-notifier* daemon

Methods:

====== =======================
Email  Send email message
File   Write subject to file
====== =======================

Forms
=====
Setup
=====
Users
-----
Permissions
^^^^^^^^^^^
======= ========================================
add     auth | user | Can add user
change  auth | user | Can change user
delete  auth | user | Can delete user
======= ========================================

Groups
------
Permissions
^^^^^^^^^^^
======= ========================================
add     auth | group | Can add group
change  auth | group | Can change group
delete  auth | group | Can delete group
======= ========================================

Languages
---------
Permissions
^^^^^^^^^^^
======= ========================================
add     main | Language | Can add Language
change  main | Language | Can change Language
delete  main | Language | Can delete Language
======= ========================================

MIME Types
----------
Database of file extension to MIME type mappings.
Used to set up valid Content-Type for downloadable
files and attachments (i.e. Knowledge Base attachments)

Permissions
^^^^^^^^^^^
======= ========================================
add     main | MIME Type | Can add MIME Type
change  main | MIME Type | Can change MIME Type
delete  main | MIME Type | Can delete MIME Type
======= ========================================

Configs
-------
Configuration files editor.

Permissions
^^^^^^^^^^^
======= ========================================
change  Superuser
======= ========================================

Documentation
=============
Administrator's Guide
---------------------
Permissions
^^^^^^^^^^^
======= ========================================
preview ANY
======= ========================================

User's Guide
------------
Permissions
^^^^^^^^^^^
======= ========================================
preview ANY
======= ========================================

Permissions
^^^^^^^^^^^
======= ========================================
preview ANY
======= ========================================

Reports
=======
Backups Status
--------------
Permissions
^^^^^^^^^^^
======= ========================================
preview ANY
======= ========================================

Lines of code
-------------
Permissions
^^^^^^^^^^^
======= ========================================
preview ANY
======= ========================================

System version
--------------
Permissions
^^^^^^^^^^^
======= ========================================
preview ANY
======= ========================================

Permissions
^^^^^^^^^^^
======= ========================================
preview ANY
======= ========================================

Periodic Tasks
==============
main.backup
-----------

main.cleanup_sessions
---------------------
