# How to add devices from network scan process

Sometimes it's usefull to add devices from network scanning process. It saves time, but also require some knowledge about NOC's basics.


## Examples:

Command context: `cd /opt/noc`
Command help:

`./noc network-scan --help`

!All args must be before address/network.


1. Single address scanning:
	`./noc network-scan 172.24.12.2`

```
ver.16            <--- Version of script
enable_ping  1    <--- Number of devices with successful ICMP responce
enable_snmp  0    <--- Number of devices with successful SNMP responce
IP;Available via ICMP;IP enable;is_managed;suggest name;SMNP sysname;SNMP sysObjectId;Vendor;Model;Name;pool;labels  <--- Head of "table"
172.24.12.2;True;True;True;172.24.12.2;None;None;None;None;campus12-14.sw;default;autoadd    <---result of scanning.

```
Device with ip `172.24.12.2` is icmp available, exists in NOC, have is_managed check and etc.

2. Network scanning:
	`./noc network-scan 172.24.12.0/30`

```
ver.16
enable_ping  2
enable_snmp  0
IP;Available via ICMP;IP enable;is_managed;suggest name;SMNP sysname;SNMP sysObjectId;Vendor;Model;Name;pool;labels
172.24.12.2;True;True;True;172.24.12.2;None;None;None;None;campus12-14.sw;default;autoadd
172.24.12.3;True;True;True;172.24.12.3;None;None;None;None;campus12-11.sw;default;autoadd
172.24.12.1;True;True;True;172.24.12.1;None;None;None;None;campus12.sw;default;autoadd
```

3. Scanning from file:
	`./noc network-scan --in /tmp/scan_input`
where: 
```
cat /tmp/nettest
172.24.12.3
172.24.12.4
172.24.12.5
```

4. Exclude some addresses from scanning:
	`./noc network-scan --in /tmp/scan_exclude`

Can combine with other arguments. For example if you want do exclude default gateway of some networks, use this command.

5. Use custom community for checks:
	`./noc network-scan --community=ofcnotpublic 172.24.12.0/30`

Default community is "public"

6. Use specific SNMP version for checks:
	`./noc network-scan --community=ofcnotpublic --version=1 172.24.12.0/30`

7. Autoadd results inside NOC:
	`./noc network-scan --community=ofcnotpublic --autoadd 172.24.12.0/30`

Before adding devices it's recommended to view on results without this key.
By default, ManagedObject's name wil be an IP address, and all other parameters such as:
	- Administrative Domain
	- Managed Object Profile
	- Network Segment
	- Pool
	- Syslog Source address
	- Trap Source address
	and etc will be "default" or "disable"

8. Custom MO parameters:

	```
	--adm-domain="MyAdmDomain"
	--obj-profile="MyMoObjProfile"
	--segment="MyNetSegment"
	--pool="MyPool"
	--syslog-source=m (management address) or --syslog-source=a (all addresses)
	--trap-source=m (management address) or --syslog-source=a (all addresses)
	```

9. Try to guess MO name from SNMP device name or PTR DNS record:

	```
	--resolve-name-snmp         Try to read from SNMP
	--resolve-name-dns			Try to request from DNS PTR
	```
	If both keys found smth, snmp answer wins. If both keys didn't found anything, IP address will be used as ManagedObject Name

10. Use NOC's Credential Profile ( Service Activation / Setup / Credential Check Rules )
	
	`--credential="MyCredentialRules"`
	It's possible use NOC's Credential Check Rules object with credential that usually works in Discovery suggest process.

11. Add label to all newly created managed objects:
	
	`--label="autoadd"`

12. Send result on email or notification group
	
	```
	--mail="MyNotificationGroup"   		Group must exists in NOC
	--email="mylovely@email.com"		Any email will be send by mailsender service, so it should have proper settings.
	```

13. Use custom format of mail:
	
	```
	--formats=csv or --formats=xlsx
	```
