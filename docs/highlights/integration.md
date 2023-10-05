# Integration

Telecom IT infrastructures tend to grow very complex and it is
hard to believe that one system can cover all processes and tasks.
NOC covers following areas:

* Network Resource Inventory (NRI)
* IP Address Management (IPAM)
* Fault Management (FM)
* Performance Management (PM)
* Configuration Management (CM)
* Service Activation (SA)

NOC designed to play nice with others and provides API for integration
with neighbor systems:

* Extract-Transfer-Load (ETL) to import data from external NRI systems.
NOC is able to synchronize data with multiple NRI systems.
* TT integration API for alarm escalation to external TT system. NOC can
escalate to multiple TT systems, depending on policy settings.
* [DataStream API](../datastream-api-reference/index.md) - high-performance near-realtime data export to external
systems. NOC can collect and provide actual network state for external
analysis and processing.
* North-bound Interface (NBI) - exposes large set of NOC functions to external systems
* Authentication API - allows to intergrate NOC installation to existing AAA
systems like Active Directory (AD), LDAP, RADIUS. NOC is able to authenticate
against multiple systems.
* External Storage API - allows to upload device configuration to external
storages using FTP, SCP, S3.

NOC integration API is widely used for modelling, data quality management (DQM),
data reconciliation (DR), Service Quality Management (SQM).

## See Also

* [NBI API Reference](../nbi-api-reference/index.md)
* [DataStream API Reference](../datastream-api-reference/index.md)