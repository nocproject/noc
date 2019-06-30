.. _config-mongo:

mongo
-----


.. _config-mongo-addresses:

addresses
~~~~~~~~~

==================  ============================================
**YAML Path**       mongo.addresses
**Key-Value Path**  mongo/addresses
**Environment**     NOC_MONGO_ADDRESSES
**Default Value**   ServiceParameter(service='mongo', wait=True)
==================  ============================================


.. _config-mongo-db:

db
~~

==================  ============
**YAML Path**       mongo.db
**Key-Value Path**  mongo/db
**Environment**     NOC_MONGO_DB
**Default Value**   noc
==================  ============


.. _config-mongo-user:

user
~~~~

==================  =================
**YAML Path**       mongo.user
**Key-Value Path**  mongo/user
**Environment**     NOC_MONGO_USER
**Default Value**   StringParameter()
==================  =================


.. _config-mongo-password:

password
~~~~~~~~

==================  ==================
**YAML Path**       mongo.password
**Key-Value Path**  mongo/password
**Environment**     NOC_MONGO_PASSWORD
**Default Value**   SecretParameter()
==================  ==================


.. _config-mongo-rs:

rs
~~

==================  =================
**YAML Path**       mongo.rs
**Key-Value Path**  mongo/rs
**Environment**     NOC_MONGO_RS
**Default Value**   StringParameter()
==================  =================


.. _config-mongo-retries:

retries
~~~~~~~

==================  =================
**YAML Path**       mongo.retries
**Key-Value Path**  mongo/retries
**Environment**     NOC_MONGO_RETRIES
**Default Value**   20
==================  =================


.. _config-mongo-timeout:

timeout
~~~~~~~

==================  =================
**YAML Path**       mongo.timeout
**Key-Value Path**  mongo/timeout
**Environment**     NOC_MONGO_TIMEOUT
**Default Value**   3s
==================  =================


.. _config-mongo-retry_writes:

retry_writes
~~~~~~~~~~~~

==================  ======================
**YAML Path**       mongo.retry_writes
**Key-Value Path**  mongo/retry_writes
**Environment**     NOC_MONGO_RETRY_WRITES
**Default Value**   False
==================  ======================


.. _config-mongo-app_name:

app_name
~~~~~~~~

==================  ==================
**YAML Path**       mongo.app_name
**Key-Value Path**  mongo/app_name
**Environment**     NOC_MONGO_APP_NAME
**Default Value**   StringParameter()
==================  ==================


.. _config-mongo-max_idle_time:

max_idle_time
~~~~~~~~~~~~~

==================  =======================
**YAML Path**       mongo.max_idle_time
**Key-Value Path**  mongo/max_idle_time
**Environment**     NOC_MONGO_MAX_IDLE_TIME
**Default Value**   60s
==================  =======================


