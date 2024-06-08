# Vendor-Agnostic"

Vendor lock is a common pitfall in telecom world. Vendors are happy
to supply not only equipment and services, but numerous software
for _configuration_ and _monitoring_. Though various EMS and NMS
may be excellent by they own, they can pose very serious problem -
network management infrastructure and maintenance processes fragmentation.

Suppose vendor _Hu_ provides excellent NMS, dealing its best with their
equipment, while vendor _Ci_ provides various EMSes with descent Motif
interface for their equipment. We must admit both systems are good,
but following aspects will arise quickly:

* Additional license penalty is common. Usually you must pay not only for equipment itself,
but for adding its equipment to NMS too.
* Processes fragmentation. All jobs with _Hu_ must be performed via their NMS,
all jobs with _Ci_ must be performed via their EMSes. So we must fragment
our staff to _Hu_ and _Ci_ experts, or demand the expertise not only
in equipment of both vendors, but in various software too
* User interfaces are inconsistent: web in one case, java ui in another,
motif on Solaris in third
* Alarms space split. _Hu_ alarms in first system, while _Ci_ alarms in another.
No correlation between systems, no proper root-cause analysis. Staff
must analyze and correlate alarms between all systems.
* Integration is technically possible, but practically costs alot. Many vendors
tend to license NBI interfaces separately.
Costs tends to rise quickly with increasing amount of system. And integration
itself imposes additional maintenance costs.

NOC, as a vendor-independentent project opens another way. Our virtues are:

* NOC has strict sepatation between device-dependent and device-independentent
parts with strict contract between them. Only hardware integration layer is device-dependent, while
all core services is device-independentent
* All vendors are equal and must be aligned to common denominator
* NOC tells with equipment using native language. No various protocol
gates like SNMP-to-CLI. If equipment provides MML, NOC will speak this
dialect of MML
* NOC provides simple and clean API for hardware integration
* As open-source project NOC leverages community cooperation. DevTeam
offers cooperation to early adopters of new platforms and helps
to integrate then with NOC

To this time NOC supports over [100 vendors](../profiles-reference/index.md)
and this list is growing quickly
