# How to Import MIB Files

MIB files contain information to resolve binary (octet-stream) values into the human-readabke format.
NOC uses MIBs to:

* Decode binary values in the SNMP traps
* In the SA scripts to convert symbolic oid names into the plain oids

!!! warning

    NOC uses `smidump` and `smilint` utilities for import, so you need 
    all dependent MIB files to be present.

## Prerequisites

* Install `smidump` and `smilint` utilities into the system (`netsnmp-utils` for the Debian-based systems)
* Check all required MIB files. `netsnmp-utils` packet istalls standard MIBs into
  the `/usr/share/mibs/ietf/` directory.
* To import MIB through web-interface deploy [mib][mib] service (via Tower)

## Preparation

We need to prepare the infrastructure to import MIB

!!! note

    In case of multi-node installation all operations must be performed on the
    node with the service [mib][mib]

Check utilities availability:

```
# smidump -v
smidump 0.4.8
# smilint -v
smilint 0.4.8
```

Check file `etc/settings.yml` is present, or create new, if neccessary.
Add following section:

``` yaml
path:
  mib_path: /usr/share/mibs/ietf/:/usr/share/mibs/site/:/opt/noc/var/mibs/dist/
  smilint: /usr/bin/smilint
  smidump: /usr/bin/smidump
```

!!! note

    Your system's paths may vary

Place all MIB file dependencies into the one of the `mib_path` directories.
For example, `/usr/share/mibs/site`.

Install NOC-supplied MIB files:

```
./scripts/deploy/install-packages requirements/mib.json
```

## Import MIB file via Web Interface

!!! note

    Ensure the [mib][mib] service is deployed and running.

1. Open `Fault Management > MIB` page in the interface.
2. Press **Add** button.
3. Choose the file and dependencies (when necessary) into the **MIB** form.
4. Press **Upload** button.

## Import MIB via CLI

```
./noc mib --local import <path>
```

where `<path>` is the path to the MIB file or to directory with MIB files.

!!! note

    The `--local` key skips the usage of the [mib][mib] service.

If the output ends with `Pass MIB through smilint to detect missed modules`,
place all missed MIB modules into one of the `mib_path` directories and repeat the command.

Otherwise, import completed successfully.

## Checking MIB

Check MIB in the web interface: `Fault Management > MIBs`

## Applying Changes

Restart [classifier][classifier] service to apply changes.

[mib]:../services-reference/mib.md
[classifier]:../services-reference/classifier.md