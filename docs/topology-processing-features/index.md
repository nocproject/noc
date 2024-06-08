# Capabilities of NOC with Topology

One of the key components of NOC is network topology. It is represented as a connectivity graph of equipment (`ManagedObject`). Based on this, the system can change its behavior, providing the following capabilities:

* Building an L2 topology based on data from equipment and external systems (`Remote System`).
* Creating L2 connections between interfaces of the device [ManagedObject](../concepts/managed-object/index.md).
* Displaying the topology on the network map.
* Determining the causes of incidents based on topology.
* Performing pathfinding based on topology.
* Generating reports based on topology data.
* Providing topological information through the `API` - [Datastream](../datastream-api-reference/managedobject.md).

L2 topology (`L2 Topology`) is built between the interfaces [Interface](../concepts/interface/index.md) of the device [ManagedObject](../concepts/managed-object/index.md). In addition to manual link creation (`Link`) through the user interface, the system can establish connections based on equipment data. The following stages of working with topology can be distinguished:

* Establishing connections between devices (manually or based on polling results).
* Calculating the uplink direction.
* Displaying the network diagram.
* Building a path based on topology.

## Building Topology

When building a topology, it's important to keep in mind the following terms:

* **Link** (`Link`) - a pair (traditionally 2).
* **Current Device** - the device (`ManagedObject`) on which the polling is running.
* **Neighboring Device** (neighbor) - devices directly connected to the current device (not through other L2 devices). They are displayed in the device's neighbor table.
* **Device Identifier** - a property that allows finding the neighboring device. The following identifiers are used in topological protocols:
    * Device MAC address (`Chassis ID`).
    * Hostname of the device.
    * IP address (`IP address`).
    * Serial number (`Serial`).
* **Device Port Identifier** - used to determine the port to which the link is connected. For example:
    * Interface name (`Interface Name`).
    * Description (`Description`).
    * Interface MAC address.
    * SNMP index (`ifindex`).
    * Interface number.
    * Others.
* **Topology Method** (`Topology Method`) - the method by which the system establishes a link. In addition to the standard methods aligned with topological protocols, the system has several additional methods.

To create a link (`Link`), it is mandatory to have an [Interface](../concepts/interface/index.md) on all connected devices. The further requirements vary depending on the method of creating a link (`Link`). Let's consider the available methods.

### Manual Link Creation

This is done through the interface panel on the [ManagedObject]() device form. To do this, select the interface of the current device and specify the interface of the neighbor with which the link will be created.

### Creating Links Based on Neighbor Protocols

For automatic link creation, you can use information about neighbors from the device. NOC supports a fairly large number of neighbor protocols, such as `LLDP`, `CDP`, ... but the basic approaches in their operation remain the same:

* The device must support the ability to display a list of neighbors along with their interfaces.
* The identifier of the neighbor from the list should allow finding the device in the system.
* The identifier of the neighbor's port should allow finding the neighbor's port in the system.
* In the [SA Profile](../concepts/sa-profile/index.md) profiles of devices, scripts for obtaining information about neighbors must be implemented.

### Link Creation Procedure

``` mermaid
flowchart TD
    discovery_start[Start Polling] --> get_lo_neighbor[Request Neighbors from Device];
    get_lo_neighbor --> find_lo_neighbor[Find Neighbor in System];
    find_lo_neighbor --> find_lo_neighbor_cond{Found Neighbor?};
    find_lo_neighbor_cond --> |Yes| find_lo_neighbor_ri[Find Neighbor's Interface in System];
    find_lo_neighbor_ri --> find_lo_neighbor_ri_cond{Found Neighbor's Interface?};
    find_lo_neighbor_ri_cond --> |Yes| get_ri_neighbor[Request Neighbors of Neighbor];
    get_ri_neighbor --> find_ro_neighbor[Find Neighbor of Neighbor in System];
    find_ro_neighbor --> find_ro_neighbor_cond{Found Current Device?};
    find_ro_neighbor_cond --> |Yes| find_ro_neighbor_ri[Find Current Device's Interface in System];
    find_ro_neighbor_ri --> find_ro_neighbor_ri_cond{Found Local Interface?};
    find_lo_neighbor_ri_cond --> |No| next_condition{Are There More Neighbors?};
    find_lo_neighbor_cond --> |No| next_condition;
    find_ro_neighbor_ri_cond --> |No| find_li_ri_cond{Is Found Interface the Same as Local?};
    find_ro_neighbor_ri_cond --> |No| next_condition;
    find_li_ri_cond --> |Yes| create_link[Create Link];
    find_li_ri_cond --> |No| next_condition;
    next_condition --> |Yes| find_lo_neighbor;
    next_condition --> |No| discoveryend[End of Polling];
```

#### Request Neighbors from Device

At the first stage, polling is initiated on the device using one of the methods. The system obtains a list of neighbors of the `current device` (the device on which the polling is running). The list includes:

* `Neighbor Identifier` - depends on the protocol. For `LLDP`, it can be the `MAC` address or `hostname`.
* `Local Port` - the port of the `current device` through which the neighbor is visible.
* `Neighbor's Port` - indicates the port of the neighboring device through which the current device is visible. It can be provided as a name, MAC address, or some local identifier (usually `snmp_index`).

Example output for `LLDP` (it will be different for other protocols):

``` json
[
    {
        "local_interface": "GigabitEthernet0/0/1",
        "neighbors": [
            {
                "remote_chassis_id_subtype": 4,
                "remote_chassis_id": "00:0E:5E:11:22:77",
                "remote_port_subtype": 5,
                "remote_port": "port 25",
                "remote_port_description": "TRUNK",
                "remote_system_name": "782-swc1",
                "remote_system_description": "ISCOM2128EA-MA-AC ROS_4.15.1365_20171229(Compiled Dec 29 2017, 15:40:31)",
                "remote_capabilities": 4
            }
        ]
    },
    {
        "local_interface": "XGigabitEthernet0/1/1",
        "neighbors": [
            {
                "remote_chassis_id_subtype": 4,
                "remote_chassis_id": "08:19:A6:11:22:88",
                "remote_port_subtype": 5,
                "remote_port": "XGigabitEthernet0/1/2",
                "remote_port_description": "\"link to WAN\"",
                "remote_system_name": "70-swc71",
                "remote_system_description": "S5328C-EI-24S",
                "remote_capabilities": 20
            }
        ]
    }
]
```

!!! note
    To reduce the frequency of device access, it is possible to configure neighbor cache.

#### Formation of Candidate List

Based on the received list of identifiers, a search is conducted for the neighboring device [ManagedObject](../concepts/managed-object/index.md) 
and its port [Interface](../concepts/interface/index.md). 
Upon success, the pair `current device -> port, neighboring device -> neighboring port` is added to the candidate list. 
After the candidate list is formed, the system begins its verification - it requests the neighbor table of the *neighboring device* 
and checks what *current device* is located behind the specified *neighboring port*.

In this case, the following errors are possible: ...

#### Link Creation

In the event of confirmation, the link creation procedure (`Link`) begins. It is regulated by the setting `Discovery Policy` [Discovery Policy](../concepts/interface-profile/index.md) in the interface profile (`Interface Profile`). The following options are available:

* `Ignored` - do not create a link (`Link`) with this port.
* `Create New` - do not create a link if one already exists.
* `Replace` - create a link with the port.
* `Cloud` - add the port to an existing link (a cloud is formed).

For the procedure itself, the following variants are possible:

* **New Link** - when there are no links on both interfaces. It is simply created (unless the `Ignored` option is set) and the `first_discovered` field is filled with the creation time.
* **Existing Link** - there is already a link between the interfaces. In this case, the `last_seen` field (the time the system last saw the link) is updated.
* **Different Link** - when there is a link on the interface, and the new one leads in a different direction. If the `Create New` option is set, the link will not be disconnected. However, if relinking (`Replace`) is allowed, behavior is regulated by the `method priority`. If a more priority method finds the link, it rebuilds it. If less priority, the link created by a higher priority method remains. The priority is set for the segment in the `Segment Profile`.

<!-- prettier-ignore -->
!!! note
    When creating a link, the `first_discovered` field is filled with the creation time. Upon rediscovery, the `last_seen` field is updated.

<!-- prettier-ignore -->
!!! note
    Removal of an existing link occurs if it is not found on the neighboring device.

#### Link Deletion

If, during the check of the neighboring device, the current device is not found among the neighbors, and there is a link (`Link`) between them, it is disconnected. However, if the device has been decommissioned or the ports are no longer in use, the link becomes "eternal" because polling cannot detect its absence due to device disconnection or the neighbor's absence. This may not always be convenient.

If there is a need to clean up links that have not been updated for a certain period, you can use the `ttl_policy` argument in the [./noc link](../man/link.md) command.

### Link Building Methods

Available methods for building links:

* Method - the method for building the link.
* Protocol - the neighbor discovery protocol used by the method.
* Script - the script required in the profile to make the method work.
* Capability - the capability required to initiate polling.

| Метод                                                         | Протокол   | Скрипт                                                                       | Caps            |
| ------------------------------------------------------------- | ---------- | ---------------------------------------------------------------------------- | --------------- |
| [CDP](../discovery-reference/box/cdp.md)                      | CDP        | [get_cdp_neighbors](../scripts-reference/get_cdp_neighbors.md)               | `Network  CDP`  |
| [REP](../discovery-reference/box/rep.md)                      | REP        | [get_rep_topology](../scripts-reference/get_rep_topology.md)                 | `Network  REP`  |
| [LLDP](../discovery-reference/box/lldp.md)                    | LLDP       | [get_lldp_neighbors](../scripts-reference/get_lldp_neighbors.md)             | `Network  LLDP` |
| [STP](../discovery-reference/box/stp.md)                      | STP        | [get_spanning_tree](../scripts-reference/get_spanning_tree.md)               | `Network  STP`  |
| [UDLD](../discovery-reference/box/udld.md)                    | UDLD       | [get_udld_neighbors](../scripts-reference/get_udld_neighbors.md)             | `Network  UDLD` |
| [OAM](../discovery-reference/box/oam.md)                      | OAM        | [get_oam_status](../scripts-reference/get_oam_status.md)                     | `Network  OAM`  |
| [BFD](../discovery-reference/box/bfd.md)                      | BFD        | [get_bfd_sessions](../scripts-reference/get_bfd_sessions.md)                 | `Network  BFD`  |
| [FDP](../discovery-reference/box/fdp.md)                      | FDP        | [get_fdp_neighbors](../scripts-reference/get_fdp_neighbors.md)               | `Network  FDP`  |
| [Huawei NDP (NTDP)](../discovery-reference/box/huawei_ndp.md) | Huawei NDP | [get_huawei_ndp_neighbors](../scripts-reference/get_huawei_ndp_neighbors.md) | `Network  FDP`  |
| [LACP](../discovery-reference/box/lacp.md)                    | LACP       | [get_lacp_neighbors](../scripts-reference/get_lacp_neighbors.md)             | `Network  LACP` |
| [NRI](../discovery-reference/box/nri.md)                      | -          | -                                                                            | -               |
| [ifDesc](../discovery-reference/box/ifdesc.md)                | -          | -                                                                            | -               |
| [xMAC](../discovery-reference/box/xmac.md)                    | -          | [get_mac_address_table](../scripts-reference/get_mac_address_table.md)       | -               |

[Segment](../discovery-reference/segment/mac.md) - a separate method for building links based on the MAC address table (`FDB`).
Unlike those listed in the table, it establishes links between devices within the same segment and operates on a segment schedule.

## Calculating Uplink Direction

A typical connectivity graph is undirected: all nodes in the graph are equal to each other. However, in real network conditions, they are divided into loosely connected clusters - [Network Segments](../concepts/network-segment/index.md). 
Connection between clusters is established through dedicated nodes (referred to as aggregators, concentrators, etc.). 
Knowing this information is important for the proper operation of [RCA](../glossary/index.md#rca) - determining the cause of failures based on topology. 
If cluster connectivity goes through a single node, its unavailability will result in the unavailability of all cluster nodes.

The system has several approaches to calculating the uplink direction. Let's take a closer look at them.

### Level

The position of a device relative to others. The higher the level, the more important the device is for the network. A device with a higher level than the current one is considered higher-level, and the uplink direction is considered to go through it. As an example, you can specify the levels of network devices based on their roles.

| Role                   | Level     |
| ---------------------- | --------- |
| **Client's Equipment** | **10-19** |
| CPE                    | 15        |
| **Access Level**       | **20-29** |
| VPN Server             | 22        |
| WiFi Access Point      | 22        |
| Media Gateway          | 23        |
| Access Switch          | 25        |
| **Aggregation Level**  | **30-39** |
| WiFi Controller        | 35        |
| Aggregation Switch     | 38        |
| **City Core**          | **40-49** |
| L3 switch/router       | 42        |
| BRAS                   | 44        |
| MPLS PE                | 44        |
| MPLS P                 | 46        |
| ASBR                   | 48        |
| **Regional Core**      | **50-59** |
| L3 switch/router       | 52        |
| MPLS PE                | 54        |
| MPLS P                 | 56        |
| ASBR                   | 58        |
| **Macroregional Core** | **60-69** |
| L3 switch/router       | 62        |
| MPLS PE                | 64        |
| MPLS P                 | 66        |
| ASBR                   | 68        |
| **National-wide Core** | **70-79** |
| L3 switch/router       | 72        |
| MPLS PE                | 74        |
| MPLS P                 | 76        |
| ASBR                   | 78        |
| **World-wide Core**    | **70-79** |
| L3 switch/router       | 82        |
| MPLS PE                | 84        |
| MPLS P                 | 86        |
| ASBR                   | 88        |

### Segment Hierarchy

In NOC, each device must have its assigned segment [Network Segment](../concepts/network-segment/index.md). 
Devices located in a parent segment relative to the segment of the device are considered higher-level, and the uplink direction is assumed to go through them.

### IP Address

As a criterion, you can use the IP address of the device. Often, higher-level devices (gateways) are assigned the lowest or highest IP address from the IP network range. This can be used...

## Settings

The polling settings for each method are located in the `Box` tab within the topology section of the [Managed Object Profile](../concepts/managed-object-profile/index.md#Box(Full_Polling)). To activate a method, you need to check the box next to it.

The requirements for each method are specified in the section. You should take into account the following requirements:

* L2 links are built between interfaces, so interface polling [Interface](../discovery-reference/box/interface.md) must be enabled for the device.
* To run the methods, they must be supported on the device, so you need to enable capability polling [Capabilities](../discovery-reference/box/caps.md). This is not required for the `ifDesc`, `xMAC`, and `NRI` methods.
* Some methods perform device lookup by identifier, so identifier polling [ID](../discovery-reference/box/id.md) must be enabled for them.

In addition to configuring polling, you must also include the method in the method priority.

### Method Priority

The configuration of priorities is located in the [Network Segment Profile](../concepts/network-segment-profile/index.md) - `Topology Building Methods`. If a device supports multiple link-building methods, a situation may arise where the information from different methods differs. For example, a link is built to one device based on the interface description (`ifDesc`), while another link is built based on `LLDP`. In this case, the method located higher in the priority list will prevail.

<!-- prettier-ignore -->
!!! note
  If a method is absent from the priority list, polling for it is not conducted.

After polling is completed, links should be built. In case of errors, they will be logged.

### Neighbor Cache

For link building, a prerequisite is its confirmation from both sides. If a device has a large number of neighbors, the confirmation procedure can lead to increased load (NOC will access the device for each neighbor during polling). To alleviate this situation, a *Neighbor Cache* is provided. When enabled for a specified time (`TTL`), the system remembers the device's neighbors and does not access it during that time. After the cache expires, accessing the device will be required during polling.

The configuration is located in the [Managed Object Profile](../concepts/managed-object-profile/index.md#Box(Full_Polling)) -> `Object Management` -> `Settings` -> `Object Profile` on the `Box` tab. By default, it is set to 0, meaning it is disabled. A value greater than 0 determines the time during which the system **memorizes the information obtained from the device** and uses it when searching for neighbors, rather than accessing the device. The use of neighbors from the cache can be seen in the polling log with the entry: `[discovery|box|<MONAME>|lldp] Use neighbors cache`.

<!-- prettier-ignore -->
!!! warning
    When the neighbor cache is enabled, new neighbors of the device will only be recognized by the system after the cache expiration. This can be misleading.

## Working with Topology

* Segment Diagram
* Path Trace to Upstream from a Card
* Path Calculation [path](../nbi-api-reference/path.md)
* RCA Calculation in Alarms [Topology Correlation](../fault-management/index.md#Topology%20Correlation)
* Reports on Metrics with Topology Consideration
