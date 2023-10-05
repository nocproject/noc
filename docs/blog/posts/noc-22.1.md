---
date: 2022-04-26
authors: [dv]
description: >
    NOC 22.1 is released.
categories:
    - General
---
In accordance to our [Release Policy](/release-policy/)
we're proudly present release [22.1](https://code.getnoc.com/noc/noc/tags/22.1).

# NOC 22.1

22.1 release contains [1329](https://code.getnoc.com/noc/noc/merge_requests?scope=all&state=merged&milestone_title=22.1) bugfixes, optimisations and improvements.

## Highlights

### Labels

NOC always has the conception of the `tags`. `Tags` are the lists of the
arbitrary strings attached to the resources. You can attach a tag to apply
the meaning  to the resources. Tags are highly controversial by their nature,
and their utility may vary from the silver bullet to the total mess.
During the release cycle, we have analyzed common problems and use-cases
and have developed several approaches to evolve the `tags` into a tool of
tremendous power. NOC 22.1 introduces the `labels`. `Labels` are the `tags`
on steroids. Just like the tags, labels are the strings, attached to the resources,
but several features change a lot:

* There is the registry of labels.
* Labels can appear in the system only via the registry.
* Labels have descriptions and color schemes.
* Labels contain permissions. Permissions define the areas the label can use
  and the directions the label can "flow"
* Group of labels may build the "Scope": Resource can have only one label from the scope.
* There are three ways to attach the label to the resource:
  
  * Manually.
  * Dynamically, following the rules.
  * Inheritance via Flow Rules. The profile and the state labels can "flow"
    to their resources.

Labels are the central core concept of the NOC. All classification tasks are
greatly simplified and two-step now: First - assign the labels, 
then - use labels for the classification.
Automation tasks can utilize the labels too - attach the proper one to alter the behavior.

### Dynamic Resource Groups

Dynamic resource groups use the labels and the classification rules to filter
the resources. The Resource Groups are the complete substitution for the
selectors from now on.

### Alarm Groups

The concept of Umbrella Alarms evolved into the Alarm Groups. An Alarm Group is an alarm that
covers one or more alarms. Alarms can participate in several groups. The NOC raises the group
alarm using the rules and clears the group automatically when it is empty.

Group alarms allow using NOC as an umbrella monitoring system, collecting alarms
from equipment and third-side NMSes directly.

### Dispose Protocol Enhancements

Correlator's "dispose" protocol now allows raising and clearing 
the alarms directly by a third party. As the result, all alarm manipulation 
logic is inside the correlator now. All alarms, including group ones, 
are handled and escalated in the same way. It removes the inconsistencies 
in handling and escalation of umbrella alarms, making the 
threshold alarms much more flexible.

As a side effect, now it is possible to create custom alarm collectors,
bridging external NMS alarms into NOC, making the NOC a full-blown
umbrella monitoring system.

### Alarm Components

Alarm Components are the bridge between an alarm and the inventory.
Components have replaced the alarm datasources and offer access
to the inventory from the alarm context.

### Metrics service

The new metrics service handles all metric processing tasks. 
There are several ways to collect metrics:

* Discovery process: Collects metrics by active equipment polling.
* metricscollector service: Accepts metrics collected by agents.
* Third-party collectors, including gRPC telemetry (planned).

metrics services:

* process the incoming stream.
* perform all necessary conversions.
* send the metrics to be written in the database.
* analyze metrics for conditions.
* raise and clear alarms.

Inside the metrics service is the Computational Direct Acyclic Graph (CDAG) -
the abstraction of the calculations. The graph represents the calculation,
where the nodes are the functions, and the edges are the calculated values.
A combination of the metrics and the complex thresholds is now possible.

NOC contains a large library of the nodes, including arithmetic operations,
algebraic functions, and window operations. Among the window functions 
is the "Gaussian Filter", sometimes known as 3-sigma. The Gaussian filter 
applies a machine-learning approach to detect proper thresholds automatically.

### Sensors

Sensors are the monitoring endpoints to measure physical values like temperature, humidity, voltage, etc. Sensors allow configuring additional
metrics collection beyond the networking metrics.

### Agent

The universal agent collects operation system metrics, data from sensors, 
and performs active measurements. The agent is lightweight and implemented 
in Rust language. The release offers collectors:

* block_io: collects block-devices input/output statistics.
* cpu: collects CPU usage statistics.
* dns: performs DNS query and collects timings.
* fs: collects file system statistics.
* http: performs HTTP/HTTPS queries  and collects timings.
* memory: collects memory usage statistics.
* network: collects network interfaces statistics.
* modbus_rtu: collects sensor data via MODBUS RTU serial protocol.
* modbus_tcp: collects sensor data via MODBUS TCP protocol
* twamp_reflector: TWAMP reflector, compatible with JUNOS and
   Cisco IOS TWAMP senders.
* twamp_sender: performs TWAMP SLA tests and collects the statistics.
  Compatible with JUNOS and Cisco IOS TWAMP reflectors.
* uptime: collects host uptime.

Agent supports zero-touch autoconfiguration with NOC zeroconf server and streams 
collected metrics to the metricscollector service.

### VLAN Management

22.1 release contains improvements to the VLAN Management:

* L2Domain: Just like VRF for IP, L2Domains define a space of unique VLAN id.
* ResourcePool: an abstraction to the resource allocation requests.
* VLAN Domain Profile and VLAN Profile as the group settings.
* Local VLAN: device-local VLAN which cannot be leaked further into the network.
  Local VLANs can overlap within L2Domain.

### Label-driven Escalation

Labels can alter the escalation process.

### Distributed Correlator

Several correlation processes can process `dispose` stream for the same pool,
removing the performance bottleneck.

### Cable Abduct Detection

Alarm processing improvements allow sophisticated use-cases.
One of them is copper cable abduction detection. The massive cable damage 
in the raiser results to time-correlated link-down events.
NOC can track such cases of abduction or vandalism to start a rapid response.

### UI Impromenents

* ExtJS IPAM
* Search managed objects by geo-address

### New Profiles

* `Linux.Astra`
* `Linux.Openwrt`
* `Meinberg.LANTIME`

### New Services

* metricscollector
* zeroconf
* metrics

## NSQ Removal

nsqd and nsqadmin are no longer used.

## Migration

* Upgrade the Tower to the latest version.
