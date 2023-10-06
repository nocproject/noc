---
date: 2020-04-01
authors: [dv]
description: >
    NOC 20.1 is released.
categories:
    - General
---
In accordance to our [Release Policy](/release-policy/)
we're proudly present release [20.1](https://code.getnoc.com/noc/noc/tags/20.1).

20.1 release contains of [254](https://code.getnoc.com/noc/noc/merge_requests?scope=all&state=merged&milestone_title=20.1) bugfixes, optimisations and improvements.
Refer to the [Release Notes](https://docs.getnoc.com/releases/20_1/)
for details.

# Highlights

## Python3 Compatibility


As it was declared in [19.4 Release Notes](https://docs.getnoc.com/releases/19_4/),
20.1 is the first release which offers full py3 compatibility. Python
version can be selected in the Tower interface during deploy.

Following Python versions are used:

* 2.7 for py2 installations
* 3.6 for py3 installations

You should stay on py2 if:

* CLIPS-based config config validation is used. You're urged to move
  to the ConfDB based validation engine.
* `custom` is used. You have to check custom code base for py3 compatibility
  with tools like `2to3` and `futurize`. It is advised to check results
  on separate test installation.
* `pyrules` are used. Just in case with `custom` you have to perform
  additional compatibility checking and testing is required.
* You have very personal reason to stay on py2.

All other installation should be deployed in py3 mode.

Please note that Python 3.7+ compatibility cannot be reached just now
due to dependencies restriction. Reaching latest stable python version
compatibility is still work in progress.

Returning to [19.4 Release Notes](https://docs.getnoc.com/releases/19_4/) -
we're starting to remove py2 compatibility code and testing infrastructure
in order to clean our codebase. NOC 20.2 will be py3-only release.

## Rust infrastructure

NOC beginning to adopt [Rust](https://www.rust-lang.org) as a
viable component of its infrastructure. Rust is blazingly fast and
memory-effective language for building reliable software. Common motivation
behind the Rust:

* No language-integrated GC, so it integrates well with Python
  via [PyO3](https://pyo3.rs) bindings. Rust can fully replace
  Cython in the NOC project. Following parts of system can gain
  great benefit from Rust:

  * ASN.1 BER decoder (SNMP Operation)
  * IP Address manipulation
  * HTTP Client

* Can be used to build high-performance existing part of the system:

  * ping
  * chwriter
  * syslogcollector
  * trapcollector

* Can be used to build like new perspective components like:

  * flowcolletor
  * cdrcollector

* Can be used to write standalone components, like server agents

Though some part of Rust usage held by py3 transition (pyo3 supports Python 3.5+),
we're expecting to remove all obstacles in 20.2 release.

We're already rewritten DNS Synchronization component from Go language
to Rust.


## Physical to Logical Interface Mapping

New mechanism called `Collator` has been introduced. Collator establishes
connection between logical interface (ManagedObject Interface)
and hardware slot bound to inventory model. So it is possible to answer the questions:

* Where particular interface is physically located?
* Has the particular interface any hardware restrictions?
* Which logical port corresponds to the physical slot?
* Which logical ports are served by given hardware module?

## Composite Connections

Inventory support for composite connections has been added.
Composite connections are physical jacks serving several ports at once.
Most known cases are RJ-21/mRJ-21, CENC-36M.
Composites are just bundle of pins assigned to several internal connections.

## NVD CPE

Inventory support for [NVD CPE](https://nvd.nist.gov/) identifiers
has been added. NOC supports CPE v2.2 and v2.3 inventory attributes.
NVD CPE identifiers allow to use NOC in security audit process.

## Serial Number Checking

Additional inventory model attributes for serial number validity
checking has been introduced. Minimal and maximal length of
serial number and regular expression pattern can be set.

Binary, broken and non-unique serial numbers are headache on
cheap optical modules, so it is good idea to drop obviously
crap serial and fallback to NOC-generated ones.

## Compare Configs

Configs from different managed objects can be compared via UI

## ./noc inventory find-serial command

Handy `find-serial` cli command has been added. It is possible
to search for one or more serials from common line and see,
where this module is located.

## SNMP Display-Hints

SNMP Display-Hints are the first-class citizens. So NOC tries to
decode binary OctetString data to the readable textual representation,
if defined by MIB or set manually during the function call.

## Task Monitor

UI to control discovery jobs has been added.

## FM Pools

Now it is possible to separate Managed Object's SA and FM pool binding.
Possible cases are:

* Intersecting address space within single segment
* Eliminating the need to allocate separate classifier/correlator
  processes for small SA pools.

## NBI getmappings API

NBI API to query object mappings has been introduced. Mappings are
relations between identifiers in NOC and in the remote systems.
Consider NOC loads Managed Object from external network inventory system (NRI)
via ETL process. NRI has own ID for the object (remote id), while NOC assigns its own (local id).
So mapping is the relation between NOC's ID, and the pairs of
(Remote System, Remote ID).

`getmappings` API allows to query objects by local or remote id and
to get all known mappings in the single call.


## Protected Fields

Some fields in UI can be marked as `protected`, preventing manual
user changes.

# Development Process Changes

## Towards Monorepo

We're beginning to collect all NOC-related repositories to a single repo.
Following repos have been merged:

* collections
* noc-sync-bind

## Flake8 Checks
  
  Codebase is clean enough to enforce previously disabled flake8 check,
so they are mandatory now:

* F403 - 'from xxx import *' used; unable to detect undefined names
* F405 - 'xxx' may be undefined, or defined from star imports: xxx
* W605 - invalid escape sequence 'x'
  
## Pending Deprecations

CLIPS-based configuration validation is not supported on python3 installations
and will be removed in NOC 20.2. Please select Python 2 if you have
config validation rules and consider to rewrite them to ConfDB validation
queries or your installation may be stuck on NOC 20.1 release.
