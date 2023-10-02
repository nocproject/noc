# Big Data
NOC collects large amount of data viable for proper
Network Management decisions, including capacity planning and
faults mitigation.

NOC splits operative (short-term) and analytic (long term) databases.
Common operations performed on operative database, optimized for
performance. Analytical data extracted from operative database,
cleaned and enriched and uploading to analytic database.

Analytic database is based on ClickHouse database and has properties:

* Columnar storage (like common BI databases)
* High level of data compression (reduced requirements to storage system)
* Sharded/Redundant to multiple nodes
* Distributed query processing
* Low IOPS, works well on common HDDs
* High read and write throughput

Analytic database structure is open and well-defined.
See [BI Models Reference](../bi-models-reference/index.md) for details.

In addition to analytic database NOC provides rich set of data
manipulation and analysis tools

* BI user interface
* ETL to populate analytic database
* Passive collectors (Syslog, SNMP Trap, NetFlow)
* Active metrics collectors during discovery
