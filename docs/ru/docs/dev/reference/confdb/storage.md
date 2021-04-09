# Config Storage

`Storing` is the process of storing device configuration in long-term storage.
NOC uses own `GridVCS` storage to store device configuration.
GridVCS is radically different from plain file system and somewhat
like version control systems (VCS), like git and mercurial.
Following `GridVCS` properties are vial for configuration processing:

* *Plug-and-play* - Available out-of-box. Do not require additional configuration or maintenance.
* *Replicated* - implemented over mongodb with replication over mongo cluster nodes
* *High-availability* - resilient to database node loss
* *Slave backup* - backup may be taken from slave
* *Versioned* - unlimited history of configuration changes. Versioning performed automatically
* *Compressed* - all data stored in compressed form
* *Lock-free* - parallel commits are safe (unkike git and mercurial)
* *Checksum protection* - every version is protected by checksum
* *Tampering protection* - extra countermeasures against intentional history rewriting.
* *Mirroring* - configurations can be uploaded to `External Storage<reference-external-storage>`.

GridVCS is provided out-of-the box and does not require additional
configuration.