---
date: 2019-07-10
---
In accordance to our [Release Policy](/blog/2018/09/12/new-release-policy/)
[we're](/devteam/) continuing support of generation of 19.1 releases. 
NOC [19.1.2](https://code.getnoc.com/noc/noc/tags/19.1.1)
collects 18 bugfixes, optimization and improvements, while fully
preserves 19.1 API.

# Migration
Migration from 19.1 release is straightforward. Just deploy 
`19.1.2` or `stable-19.1` tags from Tower.

# Improvements

| MR            | Title                                                 |
| ------------- | ----------------------------------------------------- |
| {{<mr 2006>}} | noc/noc#1032                                          |
| {{<mr 2020>}} | Add autowidth column option to ReportLinkDetail.      |
| {{<mr 2021>}} | Add autowidth column to ReportIfacesStatus.           |
| {{<mr 2023>}} | Add autowidth column option to ReportAlarmDetail.     |
| {{<mr 2039>}} | Add frozen first row in Detail Report.                |
| {{<mr 2041>}} | Add subscribers profile filter to AlarmDetail Report. |
| {{<mr 2065>}} | ensure-indexes: Create index on fm.Uptime             |
| {{<mr 2112>}} | noc/noc#914 Return first find profile that loader.    |
| {{<mr 2132>}} | Update Angtel.Topaz profile                           |

# Bugfixes

| MR            | Title                                                |
| ------------- | ---------------------------------------------------- |
| {{<mr 1847>}} | Fix DLink.DVG.get_chassis_id script                  |
| {{<mr 1952>}} | Fix SKS.SKS.get_interfaces script                    |
| {{<mr 2007>}} | Fix SKS.SKS.get_spanning_tree script                 |
| {{<mr 2008>}} | Fix Alstec.24xx.get_interfaces script                |
| {{<mr 2017>}} | Fix Huawei.VRF.get_interfaces untagged from pvid.    |
| {{<mr 2037>}} | Fix Generic.get_capabilities script when SNMP false. |
| {{<mr 2128>}} | Fix Eltex.MES profile                                |
| {{<mr 2191>}} | Fix Cisco.IOSXR.convert_interface_name               |

# Code Cleanup

| MR            | Title                           |
| ------------- | ------------------------------- |
| {{<mr 2060>}} | Remove urllib usage in profiles |
