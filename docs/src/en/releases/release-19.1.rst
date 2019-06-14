.. _release-19.1:

========
NOC 19.1
========

In accordance to our :ref:`Release Policy <releases-policy>`
`we're <https://getnoc.com/devteam/>` proudly present release `19.1 <https://code.getnoc.com/noc/noc/tags/19.1>`_.

19.1 release contains of 272 bugfixes, optimisations and improvements.

Highlights
----------

Usability
^^^^^^^^^
NOC Theme
"""""""""
19.1 introduces genuine NOC theme intended to replace venerable
ExtJS' *gray*. New flat theme is based upon Triton theme using
NOC-branded colors. NOC theme can be activated via config on per-installation basis.
We expect to make it default several releases later.

Collection Sharing
""""""""""""""""""
`Collections <https://code.getnoc.com/noc/collections>`_ is the viable part
of NOC. We're gracefully appreciate any contributions. In order to make
contribution process easier we'd added *Share* button just into JSON preview.
Enable collections sharing in config and create collections Merge Requests
directly from NOC interface by single click.

New fm.alarm
^^^^^^^^^^^^
Alarm console was thoroughly reworked. Current filters settings
are stored in URL and can be shared with other users. Additional
filters on services and subscribers were also added.

New runcommands
^^^^^^^^^^^^^^^
*Run Commands* interface was simplified. Left panel became hidden
and working area was enlarged.
List of objects can be modified directly from commands panel.
Configurable command logging option was added to :ref:`mrt service <service-mrt>`
service.

Alarm acknowledgement
^^^^^^^^^^^^^^^^^^^^^
Alarms can be acknowledged by user to show that alarm has been seen
and now under investigation.

Integration
^^^^^^^^^^^
We continue to move towards better integration with external systems.
Our first priority is clean up and document API to be used
by external systems to communicate with NOC.

NBI
"""
A new :ref:`nbi service <services-nbi>` has introduced. nbi service
is the host for Northbound Interface API, allowing to access NOC's data
from upper-level system.

:ref:`objectmetrics API <api-nbi-objectmetrics>` for
requesting metrics has introduced

DataStream
""""""""""
:ref:`DataStream service <services-datastream>` got a lots of
improvements:

* :ref:`alarm datastream <api-datastream-alarm>` for realtime alarm status streaming
* :ref:`managedobject datastream <api-datastream-managedobject>` got *asset* part
  containing hardware inventory data

API Key ACL
"""""""""""
:ref:`API Key <reference-apikey>` got and additional ACL,
allowing to restrict source addresses for particular keys.

Threshold Profiles
^^^^^^^^^^^^^^^^^^
Threshold processing became more flexible. Instead of four fixed
levels (Low error, low warning, high warning and high error)
an arbitrary amount of levels can be configured via Threshold Profiles.
Arbitrary actions can be set for each threshold violation, including:

* raising of alarm
* sending of notification
* calling handlers

Threshold closing condition can differ from opening one, allowing
`hysteresis <https://en.wikipedia.org/wiki/Hysteresis>`_ to suppress
unnecessary flapping.

.. _release-19.1-syslog-archive:

Syslog archiving
^^^^^^^^^^^^^^^^
Starting from 19.1 NOC can be used as long-term syslog archive solution.
ManagedObjectProfile got additional *Syslog Archive Policy* setting.
When enabled, :ref:`syslogcollector <service-syslogcollector>`
service mirrors all received syslog messages to long-term analytic
ClickHouse database. ClickHouse supports replication, enforces
transparent compression and has very descent IOPS requirements,
making it ideal for high-load storage.

Collected messages can be queried both through
BI interface and direct SQL queries.

STP Topology metrics
^^^^^^^^^^^^^^^^^^^^
STP topology changes metrics supported out-of-box. Devices' dashboards
can show topology changes on graphs and further analytics can be applied.
In combination with BI analytics network operators got the valuable
tool to investigate short-term traffic disruption problems in large networks.

New platform detection policy
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Behavior on new platform detection became configurable. Previous
behavior was to automatically create platform, which can lead
to headache in particular cases. Now you have and options
configured from Managed Object Profile:

* *Create* - preserve previous behavior and create new platform automatically (default)
* *Alarm* - raise umbrella alarm and stop discovery

Firmware Policy
^^^^^^^^^^^^^^^
Behavior on firmware policy violation also became configurable. ManagedObjectProfile
allow to configure following options:

* *Ignore* - do nothing (default)
* *Ignore&Stop* - Stop discovery
* *Raise Alarm* - Raise umbrella alarm
* *Raise&Stop* - Raise umbrella alarm and stop discovery

New Profiles
^^^^^^^^^^^^
19.1 contains support for TV optical-to-RF converters widely used
in cable TV networks. 2 profiles has introduced:

* IRE-Polus.Taros
* Vector.Lambda

In addition, an :ref:`NSM.TIMOS <profile-NSM.TIMOS>` profile became available

Performance, Scalability and optimisations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Caps Profile
""""""""""""
:ref:`caps discovery <discovery-box-caps>` used to collect all known capabilities for platform.
Sometimes it is not desired behavior. So *Caps profiles* are introduced.
*Caps Profiles* allows to enable or disable particular group of capabilities checking.
Group of capabilities can be explicitly enabled, disabled or enabled
only if required for configured topology discovery.

High-precision timers
"""""""""""""""""""""
19.1 contains `time.perf_counter` backport to Python 2.7. `perf_counter`
uses CPU counters to measure time intervals. It's about 2x faster
than `time.time` and allows more granularity in time interval measurements
(`time.time` changes only ~64 times per second). This greatly increases
precision of span interval measurements and of ping's RTT metrics.

Pymongo connection pool tuning
""""""""""""""""""""""""""""""
Our investigations showed that current pymongo's connection
pool implementation has design flaw that leads to *Pool connection poisoning*
problem under the common NOC's workfload: once opened mongo connection
from discovery never been closed, leaving lots of connection after
the spikes of load. We'd implemented own connection pool and
submitted pull request to pymongo project
(`See LIFO connection pool policy <https://github.com/mongodb/mongo-python-driver/pull/380>`_).

.. _release-19.1-clickhouse-cleanup:

ClickHouse table cleanup policy
"""""""""""""""""""""""""""""""
ClickHouse table retention policy may be configured on per-table basis.
partition dropping is automated and may be called manually or
from cron.

Redis cache backend
"""""""""""""""""""
Our investigations showed that memcached is prone to randomly
*forget* keys while enough memory is available. This leads to
random discovery job states loss, leading to resetting the state
of measured snmp counters, loosing random metrics and leaving empty gaps
in grafana dashboards. Problem is hard to diagnose and only cure
is to restart memcached process. Problem lies deeply in memcached
internal architecture and unlikely to be fixed.

So we'd introduced support for `Redis <https://redis.io/>`_ cache backend.
We'll make decision to make or not to make it default cache backend
after testing period.

SO_REUSEPORT & SO_FREEBIND for collectors
"""""""""""""""""""""""""""""""""""""""""
:ref:`syslogcollector <service-syslogcollector>` and
:ref:`trapcollector <service-trapcollector>` services
supports `SO_REUSEPORT` and `SO_FREEBIND` options for listeners.

`SO_REUSEPORT` allows to share single port by several collector'
processes using in-kernel load balancing, greatly improving
collectors' throughoutput.

`SO_FREEBIND` allows to bind to non-existing address, opening support
for floating virtual addresses for collector (`VRRP <https://en.wikipedia.org/wiki/Virtual_Router_Redundancy_Protocol>`_),
`CARP <https://en.wikipedia.org/wiki/Common_Address_Redundancy_Protocol>`_) etc),
adding necessary level of redundancy.

In combination with new :ref:`Syslog Archive <release-19.1-syslog-archive>` and
:ref:`ClickHouse table cleanup policy <release-19.1-clickhouse-cleanup>`
features NOC can be turned to high-performance syslog archiving solution.

GridVCS
"""""""
GridVCS is NOC's high-performance redundant version control system
used to store device configuration history. 19.1 release introduces
several improvements to GridVCS subsystem.

* built-in compression - though Mongo's Wired Tiger uses transparent
  compression on storage level, explicit compression on GridVCS level
  reduces both disk usage and database server traffic.

* Previous releases used mercurial's mdiff to calculate config deltas.
  19.1 uses `BSDIFF4 <http://www.daemonology.net/bsdiff/>`_ format by default.
  During our tests BSDIFF4 showed better results in speed and delta size.

* :ref:`./noc gridvcs <man-gridvcs>` command got additional `compress` subcommand, allowing
  to apply both compression and BSDIFF4 deltas to already collected data.
  While it can take a time for large storages it can free up significant
  disk space.

API improvements
^^^^^^^^^^^^^^^^
profile.py
""""""""""
:ref:`SA profiles <profiles>` used to live in `__init__.py`
file. Our code style advises to keep `__init__.py` empty for various
reason. Some features like profile loading from `custom` will not
work with `__init__.py` anyway.

So starting with 19.1 it is recommended to place profile's code into `profile.py`
file. Loading from `__init__.py` is still supported but it is a good
time to plan migration of custom profiles.

OIDRule: High-order scale functions
"""""""""""""""""""""""""""""""""""
Metrics `scale` can be defined as high-order functions, i.e.
function returning other functions. It's greatly increase flexibility
of scaling subsystem and allows external configuration of scaling processing.

IPAM `seen` propagation
"""""""""""""""""""""""
Workflow's `seen` signal can be configured to propagate up to the parent prefixes.
Address and Prefix profiles got new `Seen propagation policy` setting
which determines should or should not parent prefix will be notified
of child element seen by discovery.

Common usage pattern is to propagate `seen` to aggregate prefixes
to get notified when aggregate became used.

Phone workflow
""""""""""""""
`phone` module got full-blown workflow support. Each phone number and
phone range has own state which can be changed manually or via
external signals.

Breaking Changes
----------------

Migration
---------

New features
------------
|    MR                                                           | Title                                                                        |
| --------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| `MR1515 <https://code.getnoc.com/noc/noc/merge_requests/1515>`_ | Add *estimate* param to job command.                                         |
| `MR1525 <https://code.getnoc.com/noc/noc/merge_requests/1525>`_ | Collection sharing                                                           |
| `MR1498 <https://code.getnoc.com/noc/noc/merge_requests/1498>`_ | DataStream: *asset* part of ManagedObject                                    |
| `MR1516 <https://code.getnoc.com/noc/noc/merge_requests/1516>`_ | APIKey ACL                                                                   |
| `MR1518 <https://code.getnoc.com/noc/noc/merge_requests/1518>`_ | Add export/import to ./noc beef command.                                     |
| `MR1514 <https://code.getnoc.com/noc/noc/merge_requests/1514>`_ | Configurable behavior on new platforms and firmware policy violations        |
| `MR1512 <https://code.getnoc.com/noc/noc/merge_requests/1512>`_ | new fm-alarm                                                                 |
| `MR1508 <https://code.getnoc.com/noc/noc/merge_requests/1508>`_ | IRE-Polus.Taros profile                                                      |
| `MR1507 <https://code.getnoc.com/noc/noc/merge_requests/1507>`_ | Summary glyph display order                                                  |
| `MR1501 <https://code.getnoc.com/noc/noc/merge_requests/1501>`_ | Add Errors Out and Discards In for ddash                                     |
| `MR1595 <https://code.getnoc.com/noc/noc/merge_requests/595>`_  | Add periodic diagnostic to alarmdiagnostic.                                  |
| `MR1460 <https://code.getnoc.com/noc/noc/merge_requests/1460>`_ | ThresholdProfile: Flexible thresholds configuration                          |
| `MR1497 <https://code.getnoc.com/noc/noc/merge_requests/1497>`_ | Alarm acknowledge/unacknowledge                                              |
| `MR1491 <https://code.getnoc.com/noc/noc/merge_requests/1491>`_ | network stp topology changes on graph                                        |
| `MR1476 <https://code.getnoc.com/noc/noc/merge_requests/1476>`_ | GridVCS: bsdiff4 patches and zlib compression                                |
| `MR1432 <https://code.getnoc.com/noc/noc/merge_requests/1432>`_ | Add initial support for NSN.TIMOS profile                                    |
| `MR1475 <https://code.getnoc.com/noc/noc/merge_requests/1475>`_ | High-precision timers                                                        |
| `MR1458 <https://code.getnoc.com/noc/noc/merge_requests/1458>`_ | Add `Network | STP | Topology Changes metric`.                               |
| `MR1455 <https://code.getnoc.com/noc/noc/merge_requests/1455>`_ | CapsProfile                                                                  |
| `MR1396 <https://code.getnoc.com/noc/noc/merge_requests/1396>`_ | redis cache backend                                                          |
| `MR1404 <https://code.getnoc.com/noc/noc/merge_requests/1404>`_ | #794: IPAM `seen` propagation policy                                         |
| `MR1384 <https://code.getnoc.com/noc/noc/merge_requests/1384>`_ | card: project card                                                           |
| `MR1390 <https://code.getnoc.com/noc/noc/merge_requests/1390>`_ | #942: Remove Root container                                                  |
| `MR1352 <https://code.getnoc.com/noc/noc/merge_requests/1352>`_ | #694 ClickHouse table cleaning policy                                        |
| `MR1363 <https://code.getnoc.com/noc/noc/merge_requests/1363>`_ | Vector.Lambda profile                                                        |
| `MR1283 <https://code.getnoc.com/noc/noc/merge_requests/1283>`_ | NOC theme                                                                    |
| `MR1336 <https://code.getnoc.com/noc/noc/merge_requests/1336>`_ | OIDRule: High-order scale functions                                          |
| `MR1338 <https://code.getnoc.com/noc/noc/merge_requests/1338>`_ | #539 Syslog archiving                                                        |
| `MR1255 <https://code.getnoc.com/noc/noc/merge_requests/1255>`_ | nbi service                                                                  |
| `MR1345 <https://code.getnoc.com/noc/noc/merge_requests/1345>`_ | #497 syslogcollector/trapcollector: SO_REUSEPORT and IP_FREEBIND support     |
| `MR1252 <https://code.getnoc.com/noc/noc/merge_requests/1252>`_ | datastream: Alarm datastream                                                 |
| `MR1226 <https://code.getnoc.com/noc/noc/merge_requests/1226>`_ | #636 Phone Workflow integraton                                               |
| `MR1113 <https://code.getnoc.com/noc/noc/merge_requests/1113>`_ | Profiles should be moved to profile.py                                       |

Improvements
------------

|    MR                                                           | Title                                                                        |
| --------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| `MR1534 <https://code.getnoc.com/noc/noc/merge_requests/1534>`_ | Set default loglevel on command to info.                                     |
| `MR1535 <https://code.getnoc.com/noc/noc/merge_requests/1535>`_ | Update RU translation.                                                       |
| `MR1527 <https://code.getnoc.com/noc/noc/merge_requests/1527>`_ | FM Alarms localization                                                       |
| `MR1529 <https://code.getnoc.com/noc/noc/merge_requests/1529>`_ | Add full_name to PlatformApplication query fields.                           |
| `MR1522 <https://code.getnoc.com/noc/noc/merge_requests/1522>`_ | Update/report interface status3                                              |
| `MR1510 <https://code.getnoc.com/noc/noc/merge_requests/1510>`_ | Update DLink.DxS profile                                                     |
| `MR1556 <https://code.getnoc.com/noc/noc/merge_requests/1556>`_ | Update Rotek.BT profile (get_version)                                        |
| `MR1539 <https://code.getnoc.com/noc/noc/merge_requests/1539>`_ | Update settings by snmp requests for Dlink.DxS                               |
| `MR1500 <https://code.getnoc.com/noc/noc/merge_requests/1500>`_ | Update Juniper.JUNOS profile                                                 |
| `MR1503 <https://code.getnoc.com/noc/noc/merge_requests/1503>`_ | Speedup NetworkSegment Service Summary count.                                |
| `MR1502 <https://code.getnoc.com/noc/noc/merge_requests/1502>`_ | Update Report for Interfaces Status                                          |
| `MR1490 <https://code.getnoc.com/noc/noc/merge_requests/1490>`_ | Generic.get_chassis_id disable Multicast MAC address check.                  |
| `MR1494 <https://code.getnoc.com/noc/noc/merge_requests/1494>`_ | SKS.SKS and BDCOM.IOS config volatile.                                       |
| `MR1488 <https://code.getnoc.com/noc/noc/merge_requests/1488>`_ | Add platform to Linksys.SPS2xx profile.                                      |
| `MR1451 <https://code.getnoc.com/noc/noc/merge_requests/1451>`_ | Unified loader interface                                                     |
| `MR1485 <https://code.getnoc.com/noc/noc/merge_requests/1485>`_ | Add caps profile to managedobject profile ETL loader.                        |
| `MR1484 <https://code.getnoc.com/noc/noc/merge_requests/1484>`_ | Add to Linksys.SPS24xx platform OID                                          |
| `MR1434 <https://code.getnoc.com/noc/noc/merge_requests/1434>`_ | ./noc dnszone import: Parse complex $TTL directives                          |
| `MR1452 <https://code.getnoc.com/noc/noc/merge_requests/1452>`_ | Move methods from SegmentTopology to BaseTopology                            |
| `MR1449 <https://code.getnoc.com/noc/noc/merge_requests/1449>`_ | inv.networksegment: Bulk fields calculation                                  |
| `MR1454 <https://code.getnoc.com/noc/noc/merge_requests/1454>`_ | Add to_python method to ClickHouse model.                                    |
| `MR1466 <https://code.getnoc.com/noc/noc/merge_requests/1466>`_ | Add to Huawei.VRP profile get Serial Number attributes.                      |
| `MR1453 <https://code.getnoc.com/noc/noc/merge_requests/1453>`_ | ResourceGroup: TreeCombo                                                     |
| `MR1461 <https://code.getnoc.com/noc/noc/merge_requests/1461>`_ | Add config_volatile to Orion.NOS and SKS.SKS                                 |
| `MR1447 <https://code.getnoc.com/noc/noc/merge_requests/1447>`_ | Increase query interval for core.pm.utils function.                          |
| `MR1417 <https://code.getnoc.com/noc/noc/merge_requests/1417>`_ | Extendable Generic.get_chassis_id script                                     |
| `MR1441 <https://code.getnoc.com/noc/noc/merge_requests/1441>`_ | Add patern more to Huawei.MA5600T profile.                                   |
| `MR1440 <https://code.getnoc.com/noc/noc/merge_requests/1440>`_ | Optimize reportalarmdetail and reportobjectdetail.                           |
| `MR1439 <https://code.getnoc.com/noc/noc/merge_requests/1439>`_ | Update/eltex mes execute snmp                                                |
| `MR1437 <https://code.getnoc.com/noc/noc/merge_requests/1437>`_ | Delete aggregateinterface bi model                                           |
| `MR1420 <https://code.getnoc.com/noc/noc/merge_requests/1420>`_ | Add dynamically loader BI models.                                            |
| `MR1418 <https://code.getnoc.com/noc/noc/merge_requests/1418>`_ | RepoPreview MVVC                                                             |
| `MR1427 <https://code.getnoc.com/noc/noc/merge_requests/1427>`_ | Migrate Alstec.24xx.get_metrics to new model.                                |
| `MR1414 <https://code.getnoc.com/noc/noc/merge_requests/1414>`_ | networkx 2.2 and improvend spring layout implementation                      |
| `MR1413 <https://code.getnoc.com/noc/noc/merge_requests/1413>`_ | dns.dnsserver: Remove *sync* field                                           |
| `MR1400 <https://code.getnoc.com/noc/noc/merge_requests/1400>`_ | requests 2.20.0                                                              |
| `MR1392 <https://code.getnoc.com/noc/noc/merge_requests/1392>`_ | Diverged permissions                                                         |
| `MR1382 <https://code.getnoc.com/noc/noc/merge_requests/1382>`_ | #961 Process *All addresses* and *Loopback address* syslog/trap source types |
| `MR1408 <https://code.getnoc.com/noc/noc/merge_requests/1408>`_ | Add Generic.get_vlans and get_switchport scripts.                            |
| `MR1409 <https://code.getnoc.com/noc/noc/merge_requests/1409>`_ | Add get_lldp_snmp capabilities for Cisco.IOS                                 |
| `MR1410 <https://code.getnoc.com/noc/noc/merge_requests/1410>`_ | Change Iface Name OID for get_ifindexes Plante.WCDG profile                  |
| `MR1374 <https://code.getnoc.com/noc/noc/merge_requests/1374>`_ | migrate inv map to leafletjs                                                 |
| `MR1381 <https://code.getnoc.com/noc/noc/merge_requests/1381>`_ | #971 trapcollector: Gentler handling of BER decoding errors                  |
| `MR1371 <https://code.getnoc.com/noc/noc/merge_requests/1371>`_ | dnszone: Ignore addresses with missed FQDNs                                  |
| `MR1369 <https://code.getnoc.com/noc/noc/merge_requests/1369>`_ | Add theme variable to login page render.                                     |
| `MR1368 <https://code.getnoc.com/noc/noc/merge_requests/1368>`_ | Add "Up/10M" to reportcolumndatasource for report object detail.             |
| `MR1391 <https://code.getnoc.com/noc/noc/merge_requests/1391>`_ | CODEOWNERS file                                                              |
| `MR1353 <https://code.getnoc.com/noc/noc/merge_requests/1353>`_ | #788 Try to determine VRF's for DHCP address discovery                       |
| `MR1361 <https://code.getnoc.com/noc/noc/merge_requests/1361>`_ | DataStream: Load from custom                                                 |
| `MR1251 <https://code.getnoc.com/noc/noc/merge_requests/1251>`_ | Customized PyMongo connection pool                                           |
| `MR1397 <https://code.getnoc.com/noc/noc/merge_requests/1397>`_ | Juniper.junos                                                                |
| `MR1398 <https://code.getnoc.com/noc/noc/merge_requests/1398>`_ | auto logout remove msg                                                       |
| `MR1385 <https://code.getnoc.com/noc/noc/merge_requests/1385>`_ | Dead code cleanup                                                            |
| `MR1284 <https://code.getnoc.com/noc/noc/merge_requests/1284>`_ | runcommands refactoring                                                      |
| `MR1375 <https://code.getnoc.com/noc/noc/merge_requests/1375>`_ | Cleanup pyrule from classifier trigger.                                      |
| `MR1341 <https://code.getnoc.com/noc/noc/merge_requests/1341>`_ | theme body padding for form                                                  |
| `MR1362 <https://code.getnoc.com/noc/noc/merge_requests/1362>`_ | Add convert ifname for MA4000                                                |
| `MR1349 <https://code.getnoc.com/noc/noc/merge_requests/1349>`_ | Cleanup AlliedTelesis profiles.                                              |
| `MR1346 <https://code.getnoc.com/noc/noc/merge_requests/1346>`_ | snmp: Try to negotiate broken error_index                                    |
| `MR1344 <https://code.getnoc.com/noc/noc/merge_requests/1344>`_ | Add Interface packets dashboard in MO dash.                                  |
| `MR1318 <https://code.getnoc.com/noc/noc/merge_requests/1318>`_ | Migrate ReportProfileCheck report to ReportStat Backend.                     |
| `MR1228 <https://code.getnoc.com/noc/noc/merge_requests/1228>`_ | Move numpy import to parse_table_header in lib/text.                         |
| `MR1316 <https://code.getnoc.com/noc/noc/merge_requests/1316>`_ | Additional LLDP constants and caps conversion functions                      |
| `MR1324 <https://code.getnoc.com/noc/noc/merge_requests/1324>`_ | Add TZ parameter to NBI query.                                               |
| `MR1126 <https://code.getnoc.com/noc/noc/merge_requests/1126>`_ | #260 add password widget                                                     |
| `MR1322 <https://code.getnoc.com/noc/noc/merge_requests/1322>`_ | Add get_lldp_neighbors and get_capabilities for Qtech2500 profile            |
| `MR1264 <https://code.getnoc.com/noc/noc/merge_requests/1264>`_ | Add clean to events command.                                                 |
| `MR1307 <https://code.getnoc.com/noc/noc/merge_requests/1307>`_ | Update Alcatel.OS62xx profile                                                |
| `MR1285 <https://code.getnoc.com/noc/noc/merge_requests/1285>`_ | Hp.1910                                                                      |
| `MR1190 <https://code.getnoc.com/noc/noc/merge_requests/1190>`_ | Update Rotek.RTBSv1 profile                                                  |
| `MR1297 <https://code.getnoc.com/noc/noc/merge_requests/1297>`_ | Add Rotek.RTBSv1.get_metrics script.                                         |
| `MR1296 <https://code.getnoc.com/noc/noc/merge_requests/1296>`_ | add get_config script for Dlink.DVG profile                                  |
| `MR1291 <https://code.getnoc.com/noc/noc/merge_requests/1291>`_ | Extend job command.                                                          |
| `MR1276 <https://code.getnoc.com/noc/noc/merge_requests/1276>`_ | Add clean_id_bson to alarm datastream.                                       |
| `MR1274 <https://code.getnoc.com/noc/noc/merge_requests/1274>`_ | threadpool: Cleanup worker result just after setting future                  |
| `MR1286 <https://code.getnoc.com/noc/noc/merge_requests/1286>`_ | Add late_alarm metric to seflmon fm collector.                               |
| `MR1249 <https://code.getnoc.com/noc/noc/merge_requests/1249>`_ | Profile.cli_retries_super_password parameter                                 |
| `MR1250 <https://code.getnoc.com/noc/noc/merge_requests/1250>`_ | perm: response layout                                                        |                                      |
| `MR1229 <https://code.getnoc.com/noc/noc/merge_requests/1229>`_ | ldap: Additional check of username format                                    |
| `MR1214 <https://code.getnoc.com/noc/noc/merge_requests/1214>`_ | Add telemetry to MRT service.                                                |
| `MR1244 <https://code.getnoc.com/noc/noc/merge_requests/1244>`_ | Add physical iface count metrics to selfmon.                                 |
| `MR1216 <https://code.getnoc.com/noc/noc/merge_requests/1216>`_ | Add vv (very verbose parameter) to test command.                             |

Bugfixes
--------

|    MR                                                           | Title                                                                        |
| --------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| `MR1487 <https://code.getnoc.com/noc/noc/merge_requests/1487>`_ | Use ch_escape function on syslogcollector.                                   |
| `MR1478 <https://code.getnoc.com/noc/noc/merge_requests/1478>`_ | Fix Report Unknown Model Summary.                                            |
| `MR1477 <https://code.getnoc.com/noc/noc/merge_requests/1477>`_ | Fix Generic.get_capabilities snmp_v1                                         |
| `MR1474 <https://code.getnoc.com/noc/noc/merge_requests/1474>`_ | Fix load metric priority. Profile first, Generic second.                     |
| `MR1473 <https://code.getnoc.com/noc/noc/merge_requests/1473>`_ | Fix Radio and SLA graph template for CH use.                                 |
| `MR1481 <https://code.getnoc.com/noc/noc/merge_requests/1481>`_ | Fix displaying `platform` in some Cisco Stackable switches                   |
| `MR1479 <https://code.getnoc.com/noc/noc/merge_requests/1479>`_ | Fix Rotek RTBSv1 Tx Power metric                                             |
| `MR1438 <https://code.getnoc.com/noc/noc/merge_requests/1438>`_ | Fix Huawei.VRP.get_mac_address_table script                                  |
| `MR1422 <https://code.getnoc.com/noc/noc/merge_requests/1422>`_ | Fix MikroTik.RouterOS.get_interface_status_ex script                         |
| `MR1462 <https://code.getnoc.com/noc/noc/merge_requests/1462>`_ | Fix heavy cpu load on `show vlan` command                                    |
| `MR1469 <https://code.getnoc.com/noc/noc/merge_requests/1469>`_ | Fix Huawei.VRP.get_version SerialNumber rogue chart.                         |
| `MR1467 <https://code.getnoc.com/noc/noc/merge_requests/1467>`_ | Fix DLink.DxS profile                                                        |
| `MR1463 <https://code.getnoc.com/noc/noc/merge_requests/1463>`_ | Fix Extreme.XOS.get_interfaces script                                        |
| `MR1465 <https://code.getnoc.com/noc/noc/merge_requests/1465>`_ | Fix PrefixBookmark import loop.                                              |
| `MR1464 <https://code.getnoc.com/noc/noc/merge_requests/1464>`_ | Fix selfmon FM metric name.                                                  |
| `MR1457 <https://code.getnoc.com/noc/noc/merge_requests/1457>`_ | Fix getting single oid from multiple metrics.                                |
| `MR1444 <https://code.getnoc.com/noc/noc/merge_requests/1444>`_ | Fix Iskratel.MSAN profile                                                    |
| `MR1450 <https://code.getnoc.com/noc/noc/merge_requests/1450>`_ | Fix Orion.NOS.get_lldp_neighbors script                                      |
| `MR1433 <https://code.getnoc.com/noc/noc/merge_requests/1433>`_ | Fix Cisco.IOSXR profile                                                      |
| `MR1436 <https://code.getnoc.com/noc/noc/merge_requests/1436>`_ | Fix Cisco.NXOS.get_arp script                                                |
| `MR1448 <https://code.getnoc.com/noc/noc/merge_requests/1448>`_ | Fix c.id in card.base.f_object_location.                                     |
| `MR1445 <https://code.getnoc.com/noc/noc/merge_requests/1445>`_ | login button width fixed                                                     |
| `MR1459 <https://code.getnoc.com/noc/noc/merge_requests/1459>`_ | Lambda fix metrics                                                           |
| `MR1468 <https://code.getnoc.com/noc/noc/merge_requests/1468>`_ | Huawei.VRP.get_version strip serial number.                                  |
| `MR1435 <https://code.getnoc.com/noc/noc/merge_requests/1435>`_ | InfiNet fix __init__.py pattern_prompt                                       |
| `MR1426 <https://code.getnoc.com/noc/noc/merge_requests/1426>`_ | inv.map fix performance                                                      |
| `MR1443 <https://code.getnoc.com/noc/noc/merge_requests/1443>`_ | Fix Object.get_coordinate_zoom method.                                       |
| `MR1428 <https://code.getnoc.com/noc/noc/merge_requests/1428>`_ | Fix Huawei.MA5600T profile                                                   |
| `MR1430 <https://code.getnoc.com/noc/noc/merge_requests/1430>`_ | Fix Alstec.24xx metric name.                                                 |
| `MR1289 <https://code.getnoc.com/noc/noc/merge_requests/1289>`_ | Fix Juniper.JUNOS.get_lldp_neighbors Parameter 'remote_port' required.       |
| `MR1423 <https://code.getnoc.com/noc/noc/merge_requests/1423>`_ | Fix managedobject and object card for delete Root.                           |
| `MR1429 <https://code.getnoc.com/noc/noc/merge_requests/1429>`_ | Fix avs Object.get_address_text method                                       |
| `MR1424 <https://code.getnoc.com/noc/noc/merge_requests/1424>`_ | Fix getting container path in Alarm Web and Card.                            |
| `MR1425 <https://code.getnoc.com/noc/noc/merge_requests/1425>`_ | Fix typo in ManagedObject console UI.                                        |
| `MR1483 <https://code.getnoc.com/noc/noc/merge_requests/1483>`_ | Fix Raisecom.ROS.get_lldp_neighbors script                                   |
| `MR1395 <https://code.getnoc.com/noc/noc/merge_requests/1395>`_ | Fix container field type when remove Root.                                   |
| `MR1401 <https://code.getnoc.com/noc/noc/merge_requests/1401>`_ | ip.ipam: Fix prefix style                                                    |
| `MR1411 <https://code.getnoc.com/noc/noc/merge_requests/1411>`_ | Fix Add Objects to Maintenance from SA !582                                  |
| `MR1386 <https://code.getnoc.com/noc/noc/merge_requests/1386>`_ | fix error "Отсутствуют адреса линка" in dns.reportmissedp2p                  |
| `MR1405 <https://code.getnoc.com/noc/noc/merge_requests/1405>`_ | Fix Discovery Problem Detail report trace.                                   |
| `MR1394 <https://code.getnoc.com/noc/noc/merge_requests/1394>`_ | Fix get_lldp_neighbors by SNMP                                               |
| `MR1407 <https://code.getnoc.com/noc/noc/merge_requests/1407>`_ | Fix Plantet.WGSD Profile                                                     |
| `MR1403 <https://code.getnoc.com/noc/noc/merge_requests/1403>`_ | #976 Fix closing of already closed session                                   |
| `MR1406 <https://code.getnoc.com/noc/noc/merge_requests/1406>`_ | Fix avs environments graph tmpl 148                                          |
| `MR1402 <https://code.getnoc.com/noc/noc/merge_requests/1402>`_ | jsloader fixed                                                               |
| `MR1399 <https://code.getnoc.com/noc/noc/merge_requests/1399>`_ | Fix Ubiquiti profile and Generic.get_interfaces(get_bulk)                    |
| `MR1389 <https://code.getnoc.com/noc/noc/merge_requests/1389>`_ | Fix Report Discovery Poison                                                  |
| `MR1378 <https://code.getnoc.com/noc/noc/merge_requests/1378>`_ | Fix theme variable in desktop.html template.                                 |
| `MR1379 <https://code.getnoc.com/noc/noc/merge_requests/1379>`_ | Fix etl managedobject resourcegroup                                          |
| `MR1367 <https://code.getnoc.com/noc/noc/merge_requests/1367>`_ | Fix prompt in Rotek.RTBS.v1 profile.                                         |
| `MR1366 <https://code.getnoc.com/noc/noc/merge_requests/1366>`_ | Fix workflow CH dictionary.                                                  |
| `MR1365 <https://code.getnoc.com/noc/noc/merge_requests/1365>`_ | Fix selfmon FM collector.                                                    |
| `MR1364 <https://code.getnoc.com/noc/noc/merge_requests/1364>`_ | Fix update operation for superuser on secret field.                          |
| `MR1376 <https://code.getnoc.com/noc/noc/merge_requests/1376>`_ | noc/noc#952 Fix metric path for Environment metric scope.                    |
| `MR1310 <https://code.getnoc.com/noc/noc/merge_requests/1310>`_ | #964 Fix SA sessions leaking                                                 |
| `MR1357 <https://code.getnoc.com/noc/noc/merge_requests/1357>`_ | Natex_fix_sn                                                                 |
| `MR1355 <https://code.getnoc.com/noc/noc/merge_requests/1355>`_ | Cisco_fix_snmp                                                               |
| `MR1370 <https://code.getnoc.com/noc/noc/merge_requests/1370>`_ | Increase ManagedObject cache version for syslog archive field.               |
| `MR1356 <https://code.getnoc.com/noc/noc/merge_requests/1356>`_ | Fix Interface name Eltex.MES                                                 |
| `MR1354 <https://code.getnoc.com/noc/noc/merge_requests/1354>`_ | Fix Interface name QSW2500                                                   |
| `MR1335 <https://code.getnoc.com/noc/noc/merge_requests/1335>`_ | Fix get_interfaces, add reth aenet                                           |
| `MR1343 <https://code.getnoc.com/noc/noc/merge_requests/1343>`_ | Fix profilecheckdetail.                                                      |
| `MR1342 <https://code.getnoc.com/noc/noc/merge_requests/1342>`_ | Fix secret field.                                                            |
| `MR1351 <https://code.getnoc.com/noc/noc/merge_requests/1351>`_ | InfiNet-fix-get_version                                                      |
| `MR1350 <https://code.getnoc.com/noc/noc/merge_requests/1350>`_ | Fix get_interfaces for Telindus profile                                      |
| `MR1348 <https://code.getnoc.com/noc/noc/merge_requests/1348>`_ | Fix stacked packets graph.                                                   |
| `MR1360 <https://code.getnoc.com/noc/noc/merge_requests/1360>`_ | Fix Interface name ROS                                                       |
| `MR1326 <https://code.getnoc.com/noc/noc/merge_requests/1326>`_ | Fix ch_state ch datasource.                                                  |
| `MR1332 <https://code.getnoc.com/noc/noc/merge_requests/1332>`_ | Fix Span Card view from ClickHouse data.                                     |
| `MR1331 <https://code.getnoc.com/noc/noc/merge_requests/1331>`_ | Fix Huawei.MA5600T.get_cpe.                                                  |
| `MR1328 <https://code.getnoc.com/noc/noc/merge_requests/1328>`_ | Fix Cisco.IOS.get_lldp_neighbors regex                                       |
| `MR1327 <https://code.getnoc.com/noc/noc/merge_requests/1327>`_ | Fix get_interfaces for Rotek.RTBSv1, add rule for platform RT-BS24           |
| `MR1325 <https://code.getnoc.com/noc/noc/merge_requests/1325>`_ | Fix CLIPS engine in slots.                                                   |
| `MR1320 <https://code.getnoc.com/noc/noc/merge_requests/1320>`_ | Fix SNMP Trap OID Resolver                                                   |
| `MR1323 <https://code.getnoc.com/noc/noc/merge_requests/1323>`_ | Fix get_interfaces for QSW2500 (dowwn -> down)                               |
| `MR1269 <https://code.getnoc.com/noc/noc/merge_requests/1269>`_ | Fix Juniper.JUNOSe.get_interfaces script                                     |
| `MR1278 <https://code.getnoc.com/noc/noc/merge_requests/1278>`_ | Fix Huawei.MA5600T.get_cpe ValueError.                                       |
| `MR1314 <https://code.getnoc.com/noc/noc/merge_requests/1314>`_ | Fix Generic.get_chassis_id script                                            |
| `MR1306 <https://code.getnoc.com/noc/noc/merge_requests/1306>`_ | Fix AlliedTelesis.AT8000S.get_interfaces script                              |
| `MR1313 <https://code.getnoc.com/noc/noc/merge_requests/1313>`_ | Fix Cisco.IOS.get_version for ME series                                      |
| `MR1262 <https://code.getnoc.com/noc/noc/merge_requests/1262>`_ | Fix Raisecom.RCIOS password prompt matching                                  |
| `MR1238 <https://code.getnoc.com/noc/noc/merge_requests/1238>`_ | Fix Juniper.JUNOS profile                                                    |
| `MR1279 <https://code.getnoc.com/noc/noc/merge_requests/1279>`_ | Fixes empty range list in discoveryid.                                       |
| `MR1305 <https://code.getnoc.com/noc/noc/merge_requests/1305>`_ | Fix Rotek.RTBS profiles.                                                     |
| `MR1304 <https://code.getnoc.com/noc/noc/merge_requests/1304>`_ | Fix some attributes for Span in MRT serivce                                  |
| `MR1303 <https://code.getnoc.com/noc/noc/merge_requests/1303>`_ | Fix selfmon escalator metrics.                                               |
| `MR1300 <https://code.getnoc.com/noc/noc/merge_requests/1300>`_ | fm.eventclassificationrule: Fix creating from event                          |
| `MR1295 <https://code.getnoc.com/noc/noc/merge_requests/1295>`_ | Fix ./noc mib lookup                                                         |
| `MR1298 <https://code.getnoc.com/noc/noc/merge_requests/1298>`_ | Fix custom metrics path in Generic.get_metrics.                              |
| `MR1290 <https://code.getnoc.com/noc/noc/merge_requests/1290>`_ | Fix custom metrics.                                                          |
| `MR1225 <https://code.getnoc.com/noc/noc/merge_requests/1225>`_ | noc/noc#954 Fix Cisco.IOS.get_inventory script                               |
| `MR1275 <https://code.getnoc.com/noc/noc/merge_requests/1275>`_ | Fix InfiNet.WANFlexX.get_lldp_neighbors script                               |
| `MR1281 <https://code.getnoc.com/noc/noc/merge_requests/1281>`_ | Delete quit() in script                                                      |
| `MR1280 <https://code.getnoc.com/noc/noc/merge_requests/1280>`_ | Fit get_config                                                               |
| `MR1277 <https://code.getnoc.com/noc/noc/merge_requests/1277>`_ | Fix Zhone.Bitstorm.get_interfaces script                                     |
| `MR1254 <https://code.getnoc.com/noc/noc/merge_requests/1254>`_ | Fix InfiNet.WANFlexX.get_interfaces script                                   |
| `MR1272 <https://code.getnoc.com/noc/noc/merge_requests/1272>`_ | Fix vendor name in SAE script credentials.                                   |
| `MR1246 <https://code.getnoc.com/noc/noc/merge_requests/1246>`_ | Fix Huawei.VRP pager                                                         |
| `MR1268 <https://code.getnoc.com/noc/noc/merge_requests/1268>`_ | Fix scheme migrations                                                        |
| `MR1245 <https://code.getnoc.com/noc/noc/merge_requests/1245>`_ | Fix Huawei.VRP3 prompt match                                                 |
| `MR1259 <https://code.getnoc.com/noc/noc/merge_requests/1259>`_ | fix_error_web                                                                |
| `MR1258 <https://code.getnoc.com/noc/noc/merge_requests/1258>`_ | Fix managed_object_platform migration.                                       |
| `MR1260 <https://code.getnoc.com/noc/noc/merge_requests/1260>`_ | Fix pm.util.get_objects_metrics if object_profile metrics empty.             |
| `MR1253 <https://code.getnoc.com/noc/noc/merge_requests/1253>`_ | Fix path in radius(services)                                                 |
| `MR1203 <https://code.getnoc.com/noc/noc/merge_requests/1203>`_ | Fix prompt pattern in Eltex.DSLAM profile                                    |
| `MR1247 <https://code.getnoc.com/noc/noc/merge_requests/1247>`_ | Fix consul resolver index handling                                           |
| `MR1239 <https://code.getnoc.com/noc/noc/merge_requests/1239>`_ | #911 consul: Fix faulty state caused by changes in consul timeout behavior   |
| `MR1237 <https://code.getnoc.com/noc/noc/merge_requests/1237>`_ | #956 fix web scripts                                                         |
| `MR1221 <https://code.getnoc.com/noc/noc/merge_requests/1221>`_ | Fix Generic.get_lldp_neighbors script                                        |
| `MR1243 <https://code.getnoc.com/noc/noc/merge_requests/1243>`_ | Fix now shift for selfmon task late.                                         |
| `MR1231 <https://code.getnoc.com/noc/noc/merge_requests/1231>`_ | noc/noc#946 Fix ManagedObject web console.                                   |
| `MR1235 <https://code.getnoc.com/noc/noc/merge_requests/1235>`_ | Fix futurize in SLA probe.                                                   |
| `MR1234 <https://code.getnoc.com/noc/noc/merge_requests/1234>`_ | Fix Huawei.MA5600T.get_cpe.                                                  |
| `MR1220 <https://code.getnoc.com/noc/noc/merge_requests/1220>`_ | Fix Generic.get_interfaces script                                            |
| `MR1204 <https://code.getnoc.com/noc/noc/merge_requests/1204>`_ | Fix Raisecom.ROS.get_interfaces script                                       |
| `MR1215 <https://code.getnoc.com/noc/noc/merge_requests/1215>`_ | Fix platform field in Platform Card.                                         |
| `MR1210 <https://code.getnoc.com/noc/noc/merge_requests/1210>`_ | ManagedObject datastream: Fix *links* property. *capabilities* property      |
| `MR1212 <https://code.getnoc.com/noc/noc/merge_requests/1212>`_ | Fix save empty metrics threshold in ManagedObjectProfile UI.                 |
| `MR1211 <https://code.getnoc.com/noc/noc/merge_requests/1211>`_ | Fix interface validation errors in Huawei.VRP, Siklu.EH, Zhone.Bitstorm.     |
| `MR1317 <https://code.getnoc.com/noc/noc/merge_requests/1317>`_ | sa.managedobjectprofile: Fix text                                            |
| `MR1340 <https://code.getnoc.com/noc/noc/merge_requests/1340>`_ | noc/noc#966                                                                  |
| `MR1294 <https://code.getnoc.com/noc/noc/merge_requests/1294>`_ | selfmon typo in mo                                                           |
| `MR1105 <https://code.getnoc.com/noc/noc/merge_requests/1105>`_ | #856 Rack view fix                                                           |
| `MR1208 <https://code.getnoc.com/noc/noc/merge_requests/1208>`_ | #947 Fix MAC ranges optimization                                             |
