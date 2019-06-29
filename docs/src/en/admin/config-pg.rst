.. _config-pg:

pg
--


.. _config-pg-addresses:

addresses
~~~~~~~~~

==================  =============================================================================
**YAML Path**       pg.addresses
**Key-Value Path**  pg/addresses
**Environment**     NOC_PG_ADDRESSES
**Default Value**   ServiceParameter(service='postgres', wait=True, near=True, full_result=False)
==================  =============================================================================


.. _config-pg-db:

db
~~

==================  =========
**YAML Path**       pg.db
**Key-Value Path**  pg/db
**Environment**     NOC_PG_DB
**Default Value**   noc
==================  =========


.. _config-pg-user:

user
~~~~

==================  =================
**YAML Path**       pg.user
**Key-Value Path**  pg/user
**Environment**     NOC_PG_USER
**Default Value**   StringParameter()
==================  =================


.. _config-pg-password:

password
~~~~~~~~

==================  =================
**YAML Path**       pg.password
**Key-Value Path**  pg/password
**Environment**     NOC_PG_PASSWORD
**Default Value**   SecretParameter()
==================  =================


.. _config-pg-connect_timeout:

connect_timeout
~~~~~~~~~~~~~~~

==================  ======================
**YAML Path**       pg.connect_timeout
**Key-Value Path**  pg/connect_timeout
**Environment**     NOC_PG_CONNECT_TIMEOUT
**Default Value**   5
==================  ======================


