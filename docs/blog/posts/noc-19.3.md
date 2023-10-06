---
date: 2019-08-16
authors: [dv]
description: >
    NOC 19.3 is released.
categories:
    - General
---
In accordance to our [Release Policy](/release-policy/)
we're proudly present release [19.3](https://code.getnoc.com/noc/noc/tags/19.3).

19.3 release contains of [318](https://code.getnoc.com/noc/noc/merge_requests?scope=all&state=merged&milestone_title=19.3) bugfixes, optimisations and improvements.
Refer to the [Release Notes](https://docs.getnoc.com/master/en/releases/release-19.3.html)
for details.

# Highlights

## New Profiles

* [Extreme.Summit200](https://docs.getnoc.com/master/en/profiles/Extreme.Summit200.html)
* [Polygon.IOS](https://docs.getnoc.com/master/en/profiles/Polygon.IOS.html)
* [Eltex.WOP](https://docs.getnoc.com/master/en/profiles/Eltex.WOP.html)

## ConfDB Object and Interface Validation Policies

NOC 19.3 brings ability to validate object and interface settings
using [ConfDB Queries](https://docs.getnoc.com/master/en/dev/confdb-query.html). This feature
will became primary way of validation and will replace old
CLIPS-based implementation in NOC 19.5.

It is good time to begin legacy validation policy migrations.

## ConfDB Syntax Expansion

ConfDB got additional syntax for:

* NTP support
* Video, Audio settings and media streaming

## ConfDB 'raw' Section

Raw tokenized input can be applied to ConfDB under the `raw` node.
So platform-depended syntax can be processed via ConfDB Queries and
validators natively, even if no platform-independentent syntax exists.
`raw` section may be enabled on Managed Object Profile level.

## ConfDB 'meta' Section

NOC 19.3 adds `meta` section, containing valuable NOC database
information directly exposed to ConfDB queries. Lots of additional
information included:

* Vendor
* Platform
* Software Version
* Profile
* Administrative Domain
* Network Segment
* Managed Object Tags
* Managed Object Profile
* Interface Profile
* Interface Network Neighbors (i.e. Links)

## ConfDB Normalizers

NOC 19.3 introduces 4 new profiles:

* [Beward.BD](https://docs.getnoc.com/master/en/profiles/Beward.BD.html)
* [Cisco.IOS](https://docs.getnoc.com/master/en/profiles/Cisco.IOS.html)
* [Dahua.DH](https://docs.getnoc.com/master/en/profiles/Dahua.DH.html)
* [Hikvision.DSKV8](https://docs.getnoc.com/master/en/profiles/Hikvision.DSKV8.html)

## Uplink Policy

Uplink detection algorithm for RCA became configurable now.
Following policies may be used:

* Segment Hierarchy (previous algorithm)
* Object Level
* All Segment Objects
* Lesser Management Address
* Greater Management Address

Uplink policies may be configured at Network Segment Profile level.
Multiple policies may be used with falling back to next policy until
uplinks are detected.

Uplink policies are greatly improve the quality of topology-based RCA.
See [Uplink Policy](https://docs.getnoc.com/master/en/reference/network-segment-profile.html#uplink-policy)
for details.

## Topology RCA Optimization

Topology-based Root-Cause analysis may be resource consumption.
NOC 19.3 introduces new experimental accelerated mode
called `RCA Neighbor Cache`. Smarter data precalculation and caching
in combination of database query optimization and bulk updates
allows to achieve 2-3 times speedup on real-world installations.

To enable the feature perform following steps:

* Run fix:

   $ noc fix apply fix_object_uplinks

* Stop `correlator` processes
* Enable [enable_rca_neighbor_cache](https://docs.getnoc.com/master/en/admin/config-fm.html#enable-rca-neighbor-cache) configuration variable
* Start `correlator` processes

Warning:

    Alarm processing will be postponed when correlator process is stopped,
    so alarm creation and clearing will be delayed until the correlator
    process will be started again.

## Prometheus Histograms

Prometheus histograms and quantiles may be exported via /metrics endpoint.
Additional metrics may be enabled in config.
See [metrics section](https://docs.getnoc.com/master/en/admin/config-metrics.html) for details.

## ObjectModel Tags

Inventory models got additional marking, which may be useful in various cases.
See [ObjectModel Tags](https://docs.getnoc.com/master/en/dev/objectmodel-tags.html) for details.
Model's tags are also exposed into [managedobject DataStream](https://docs.getnoc.com/master/en/api/datastream-managedobject.html).

## Django upgrade

Previous releases of NOC relied on venerable Django 1.4 dated back to 2012.
Django's team worked hard on improving their product according to their
vision. Unfortunately they tend to introduce a lot of incompatibilities and
upgrading to each next Django's major release is the real pain.
Django 1.4 fits our needs well but is not maintained and is incompatible
with Python 3. So it is the time to to collect the pains.

We'd migrated from [1.4](https://docs.djangoproject.com/en/2.2/releases/1.4/) to [1.5](https://docs.djangoproject.com/en/2.2/releases/1.5/),
then from 1.5 to [1.6](https://docs.djangoproject.com/en/2.2/releases/1.6/),
then followed by upgrades to [1.7](https://docs.djangoproject.com/en/2.2/releases/1.7/),
[1.8](https://docs.djangoproject.com/en/2.2/releases/1.8/),
[1.9](https://docs.djangoproject.com/en/2.2/releases/1.9/),
[1.10](https://docs.djangoproject.com/en/2.2/releases/1.10/)
and stopped at [1.11](https://docs.djangoproject.com/en/2.2/releases/1.11/).
During our stroll we'd became very disappointed by Django's API stability
and the high maintenance costs for the complex applications and applied
some countermeasures.

NOC 19.3 brings following changes:

* Django 1.11.22
* Django's auth contrib package has been replaced with `AAA module`.
* `South` migrations has been replaced with our own `Migration Engine`.
* All legacy Django admin applications (ModelApplication) has been replaced with ExtJS implementations.
* Django will never create or modify database structure on its own (so-called syncdb).
* Django static media repacked as [django-media](https://code.getnoc.com/npkg/django-media) npkg package.

## AAA module

User and Groups use NOC's own implementation instead of Django's ones.
Besides the native ExtJS UI it allows future independentent development
according our needs. User Profile became the part of User model.

## Migration Engine

[South](https://south.readthedocs.io/en/latest/) database
migration engine stopped in development and users are urged to
move to Django's 1.7 built-in migration engine. During our investigations
we'd found that we need to completely rewrite 500+ of existing migrations,
migrations code will be bloated by the unnecessary abstractions and we
need to invite the way to preserve old migration history.

So we'd developed migration engine, simple but powerful. Key benefits are:

* Small, clean API.
* Semi-automatical translation of existing migration.
* Seamless migration history conversion.
* Skipped migrations with from other development branch, may be applied later.

# Development Process Changes

## Code Formatting

NOC adopts [black](https://black.readthedocs.io/en/stable/) -
the python code formatter. CI pipeline checks code formatting
of changed python files. Any misformatting considered the error
and CI pipeline fails at the [lint` stage. We recommend to
add black formatting to git's pre-commit hook or to the IDE's on-save
hook.

We'd already reformatted all ours codebase and NOC is now fully
`PEP8](https://www.python.org/dev/peps/pep-0008/)-compatible.
Docker container is also available. Use:

    docker run --rm \
        -w /src \
        -v $PWD:/src \
        registry.getnoc.com/infrastructure/black:master \
        /usr/local/bin/black <file name>

to format file

## Towards Python 3 compatibility

Python 3 compatibility became one of our priorities. With 19.3 we'd
fixed lots of incompatibilities, upgraded same dependencies
and becoming to get rid of unsupported ones.
Though a lots of work and testing still required
we're expecting to reach full Python 3 compatibility
in one of future releases.

## MR Labels

We're developed [the policy](https://docs.getnoc.com/master/en/dev/mr-labels.html) for Merge Request's (MR) labels.
CI pipeline checks the labels and fails at the `lint` stage in case of errors.
Label policy helps to organize testing and code reviewing process
and quickly explains the goals of MR and subsystems affected.

# Breaking Changes

## Explicit MongoDB Connections

Prior to 19.3 NOC relied that importing of `noc.lib.nosql` automatically
creates MongoDB connection. This kind of auto-magic used to work
but requires to access all mongo-related stuff via `noc.lib.nosql`.
Starting from 19.3 we're beginning to cleanup API and the code and demand,
that MongoDB connection is to be initialized implicitly.

For custom commands and python scripts

```
    from noc.core.mongo.connection import connect

    ...
    connect()
```

For custom services set service's `use_mongo` property to `True`

## Other Changes

* ManagedObjectSelector.resolve_expression() renamed
  to ManagedObjectSelector.get_objects_from_expression()
