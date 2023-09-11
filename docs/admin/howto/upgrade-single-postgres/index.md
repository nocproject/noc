# How to Upgrade your Singlenode PostgreSQL Server

NOC [Tower](https://code.getnoc.com/noc/tower/) isn't an instrument for upgrading your databases. 
First it's very complicated process with many pitfalls. Second we don't know your environment. 
So, you must upgrade Postgres by your own.

Here is a small manual.

## Prepare for upgrading database

1. Stop noc service
   - `systemctl stop noc`
2. Do a backup of PostgreSQL Database
   - `sudo -u postgres pg_dumpall -c -f /tmp/pg_dumpall.out -v -U postgres`
   - save backup file somewhere: `cp /tmp/pg_dumpall.out ~/`

## Upgrade database

Let assume that we want to upgrade from **9.6** to **14** version.

### RPM-based distros (Centos, RHEL, Oracle Linux)

1. Install postgresql-server of new version:
   - `yum install postgresql14-server.x86_64`
2. Init new database from new binary:
   - `/usr/pgsql-14/bin/postgresql-14-setup initdb`
3. Stop old server:
   - `systemctl stop postgresql-9.6`
4. Become `postgres` user
   - `su - postgres`
5. Check if we can upgrade this database:
   - `/usr/pgsql-14/bin/pg_upgrade --old-bindir=/usr/pgsql-9.6/bin/ --new-bindir=/usr/pgsql-14/bin/ --old-datadir=/var/lib/pgsql/9.6/data/ --new-datadir=/var/lib/pgsql/14/data/ --check`

Output example: 
```
Performing Consistency Checks on Old Live Server
------------------------------------------------
Checking cluster versions                                   ok
Checking database user is the install user                  ok
Checking database connection settings                       ok
Checking for prepared transactions                          ok
Checking for system-defined composite types in user tables  ok
Checking for reg* data types in user tables                 ok
Checking for contrib/isn with bigint-passing mismatch       ok
Checking for tables WITH OIDS                               ok
Checking for invalid "sql_identifier" user columns          ok
Checking for invalid "unknown" user columns                 ok
Checking for hash indexes                                   ok
Checking for presence of required libraries                 ok
Checking database user is the install user                  ok
Checking for prepared transactions                          ok
Checking for new cluster tablespace directories             ok

*Clusters are compatible*
```
6. Upgrade this database:
   - `/usr/pgsql-14/bin/pg_upgrade --old-bindir=/usr/pgsql-9.6/bin/ --new-bindir=/usr/pgsql-14/bin/ --old-datadir=/var/lib/pgsql/9.6/data/ --new-datadir=/var/lib/pgsql/14/data/`

Output example:
```
Performing Consistency Checks
-----------------------------
Checking cluster versions                                   ok
Checking database user is the install user                  ok
Checking database connection settings                       ok
Checking for prepared transactions                          ok
Checking for system-defined composite types in user tables  ok
Checking for reg* data types in user tables                 ok
Checking for contrib/isn with bigint-passing mismatch       ok
Checking for tables WITH OIDS                               ok
Checking for invalid "sql_identifier" user columns          ok
Checking for invalid "unknown" user columns                 ok
Creating dump of global objects                             ok
Creating dump of database schemas
                                                            ok
Checking for presence of required libraries                 ok
Checking database user is the install user                  ok
Checking for prepared transactions                          ok
Checking for new cluster tablespace directories             ok

If pg_upgrade fails after this point, you must re-initdb the
new cluster before continuing.

Performing Upgrade
------------------
Analyzing all rows in the new cluster                       ok
Freezing all rows in the new cluster                        ok
Deleting files from new pg_xact                             ok
Copying old pg_clog to new server                           ok
Setting oldest XID for new cluster                          ok
Setting next transaction ID and epoch for new cluster       ok
Deleting files from new pg_multixact/offsets                ok
Copying old pg_multixact/offsets to new server              ok
Deleting files from new pg_multixact/members                ok
Copying old pg_multixact/members to new server              ok
Setting next multixact ID and offset for new cluster        ok
Resetting WAL archives                                      ok
Setting frozenxid and minmxid counters in new cluster       ok
Restoring global objects in the new cluster                 ok
Restoring database schemas in the new cluster
                                                            ok
Copying user relation files
                                                            ok
Setting next OID for new cluster                            ok
Sync data directory to disk                                 ok
Creating script to analyze new cluster                      ok
Creating script to delete old cluster                       ok
Checking for hash indexes                                   ok
Checking for extension updates                              ok

Upgrade Complete
----------------
Optimizer statistics are not transferred by pg_upgrade so,
once you start the new server, consider running:
    ./analyze_new_cluster.sh

Running this script will delete the old cluster's data files:
    ./delete_old_cluster.sh
```

7. Start new server:
   - `systemctl start postgresql-14`
   - `systemctl status postgresql-14`

8. Remove old PG packages:
   - `yum remove postgresql96* -y`

9. Write proper new version of PostgreSQL (**14**) in the Tower in `postgres` service at `PostgreSQL version` field.
10. Deploy

### DEB-based distros (Debian, Ubuntu)

1. todo!