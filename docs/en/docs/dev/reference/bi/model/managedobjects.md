# managedobjects model

## Table Structure

| Setting    | Value                                       |
| ---------- | ------------------------------------------- |
Table Name | managedobjects
Engine|     MergeTree(date, (managed_object, ts), 8192)

Field       |              Data Type    |        Description
--- | --- | ---
date                    |  Date           |      Date
ts                      |  DateTime       |      Created
managed_object          |  UInt64         |      Object Name
administrative_domain   |  UInt64         |      Admin. Domain
segment                 |  UInt64         |      Network Segment
container               |  UInt64         |      Container
level                   |  UInt16         |      Level
x                       |  Float64        |      Longitude
y                       |  Float64        |      Latitude
pool                    |  UInt64         |      Pool Name
name                    |  String         |      Name
address                 |  UInt32         |      Address
is_managed              |  UInt8          |      Is Managed
profile                 |  UInt64         |      Profile
vendor                  |  UInt64         |      Vendor
platform                |  UInt64         |      Platform
version                 |  UInt64         |      Version
n_interfaces            |  Int32          |      Interface count
n_subscribers           |  Int32          |      Interface count
n_services              |  Int32          |      Interface count
n_neighbors             |  Int32          |      Neighbors
n_links                 |  Int32          |      Interface count
nri_links               |  Int32          |      Links (NRI)
mac_links               |  Int32          |      Links (MAC)
stp_links               |  Int32          |      Links (STP)
lldp_links              |  Int32          |      Links (LLDP)
cdp_links               |  Int32          |      Links (CDP)
has_stp                 |  UInt8          |      Has STP
has_lldp                |  UInt8          |      Has LLDP
has_cdp                 |  UInt8          |      Has CDP
has_snmp                |  UInt8          |      Has SNMP
has_snmp_v1             |  UInt8          |      Has SNMP v1
has_snmp_v2c            |  UInt8          |      Has SNMP v2c
