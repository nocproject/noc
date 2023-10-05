---
date: 2020-06-09
authors: [dv]
description: >
    NOC 20.2 is released.
categories:
    - General
---
In accordance to our [Release Policy](/release-policy/)
we're proudly present release [20.2](https://code.getnoc.com/noc/noc/tags/20.2).

20.2 release contains of [249](https://code.getnoc.com/noc/noc/merge_requests?scope=all&state=merged&milestone_title=20.2) bugfixes, optimisations and improvements.
Refer to the [Release Notes](https://docs.getnoc.com/master/releases/20_2/)
for details.

# Highlights

## Python3 Compatibility

As it was declared 20.2 is the first Python3-only release. This allows us to clean up
and optimize code base in following ways:

* All Python2 compatibility layers are removed.
* Key dependencies (Tornado, Django, etc) are upgraded to latest stable versions.
* async/await are used instead `@tornado.gen.coroutine` in all the places.
* Type annotations are heavily used in newly-introduced and in modified code.

Low-level network-handling code, including SNMP, RPC, HTTP-client and
all CLI variants are rewritten from Tornado to Python3-native asyncio.
It allows to clean up code, fix some old cryptic bugs and introduce
gentler error- and timeout- handling.

NOC 20.2 is compatible with Python 3.7 and 3.8.

So we have to admit the Python3 migration Odyssey is over. It tooks
over one year, consumes lots of work, sometimes with acrobatic exercises
to maintain compatibility and stability. But in addition to code
simplicity, stability and instrumentation we gave serious performance benefits. Our
investigations on real-world installation shows that NOC 20.2 requires
10-15% less CPU, than previous Python 2 based releases.


## Interface Description Topology Discovery

Meet the `ifdesc` topology discovery method. It is
last-resort semi-automatic method of linking based on interface
description analysis. `ifdesc` comes to resque when all other
methods failed. Operator has to define a set of regular expressions
to extract a neighbor information from descriptions and has to
configure network equipment. In contrast to manual linking,
`ifdesc` is configurable as common topology discovery method.
Its precedence over other methods can be adjusted, so its results
may be refined by more precise automatic methods (i.e. LLDP), and it can be
used to refine more error-prone methods (i.e. MAC).

`ifdesc` is the 14th topology discovery method available out of the box.


## MAC Blacklist


Costs cutting and lack of proper Q&A sometimes leads to large parties
of network equipment with non-unique MAC addresses. Overall
impact may vary: from insignificant, to ARP-cache poisoning, to inpredictable
STP topology changes. It-also affects the topology discovery methods
based on neighbor identification upon MAC address (LLDP, STP, MAC).
So its safer to maintain a list of broken MAC addresses to notify
personnel on possible problems.

MAC blacklist is maintained and distributed on deploy, like other
collections, and can be adjusted and maintained locally and shared back
to the repo.

LLDP discovery method now consults on MAC Blacklist and tries to mitigate
problem by using neighbor information from additional TLVs.


## RCA Downlink Merge Policy

Real-world networks often repeats the pattern when
aggregation switch (A) is placed on PoP with redundant reserved power
and connected to home access switches (B, C, D, E), which are
powered from non-redundant city power grid.


    graph TD;
        A --> B;
        A --> C;
        A --> D;
        A --> E;

During the maintenance on power grid, several access switches may
expect power loss, while aggregation switch stays on-line as
unaffected or switched to reserve power. Current topology-based RCA
scheme will register each access switch failure as separate root cause
alarms and will propagate them as separate trouble tickets. It may
take a time for personnel to detect all those problems are related
and inferred by power problems.

NOC 20.2 introduces additional `Downlink Merge` policy. `Downlink Merge`
is enabled on aggregation switch (A) and allows to tie all direct
children alarms together and to process and escalate them as a one failure.
Network personnel will take a hint to check alarms as related together
and will be notified to check the power.


## Multi-Format Datastreams

Datastreams can be configured to separate views, filtering or morphing
records. Views, called `formats` can be used to enrich datastreams
with data from external sources, or to restring amount of data
to be passed to external systems.

Each `format` can be configured to additional API Key role, allowing
granular access.


## Customized SNMP-response parsers

Broken SNMP implementations are in the wild. Sometimes responses
are malformed, while still containing meaningful data. So we added
`Profile.get_snmp_response_parser()` method to override default
response parser to customized one when necessary.
