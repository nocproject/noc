.. _config-Config:

Global
------

Global settings applicable to all services

.. _config-loglevel:

loglevel
~~~~~~~~

==================  ===================
**YAML Path**       loglevel
**Key-Value Path**  loglevel
**Environment**     NOC_LOGLEVEL
**Default Value**   info
==================  ===================

Possible values:

* critical
* error
* warning
* info
* debug

.. _config-brand:

brand
~~~~~

==================  =========
**YAML Path**       brand
**Key-Value Path**  brand
**Environment**     NOC_BRAND
**Default Value**   NOC
==================  =========


.. _config-global_n_instances:

global_n_instances
~~~~~~~~~~~~~~~~~~

==================  ======================
**YAML Path**       global_n_instances
**Key-Value Path**  global_n_instances
**Environment**     NOC_GLOBAL_N_INSTANCES
**Default Value**   1
==================  ======================


.. _config-installation_name:

installation_name
~~~~~~~~~~~~~~~~~

==================  =========================
**YAML Path**       installation_name
**Key-Value Path**  installation_name
**Environment**     NOC_INSTALLATION_NAME
**Default Value**   Unconfigured installation
==================  =========================


.. _config-instance:

instance
~~~~~~~~

==================  ============
**YAML Path**       instance
**Key-Value Path**  instance
**Environment**     NOC_INSTANCE
**Default Value**   0
==================  ============


.. _config-language:

language
~~~~~~~~

==================  ============
**YAML Path**       language
**Key-Value Path**  language
**Environment**     NOC_LANGUAGE
**Default Value**   en
==================  ============


.. _config-language_code:

language_code
~~~~~~~~~~~~~

==================  =================
**YAML Path**       language_code
**Key-Value Path**  language_code
**Environment**     NOC_LANGUAGE_CODE
**Default Value**   en-us
==================  =================


.. _config-listen:

listen
~~~~~~

==================  ==========
**YAML Path**       listen
**Key-Value Path**  listen
**Environment**     NOC_LISTEN
**Default Value**   auto:0
==================  ==========


.. _config-log_format:

log_format
~~~~~~~~~~

==================  ==================================
**YAML Path**       log_format
**Key-Value Path**  log_format
**Environment**     NOC_LOG_FORMAT
**Default Value**   %(asctime)s [%(name)s] %(message)s
==================  ==================================


.. _config-thread_stack_size:

thread_stack_size
~~~~~~~~~~~~~~~~~

==================  =====================
**YAML Path**       thread_stack_size
**Key-Value Path**  thread_stack_size
**Environment**     NOC_THREAD_STACK_SIZE
**Default Value**   0
==================  =====================


.. _config-gitlab_url:

gitlab_url
~~~~~~~~~~

==================  ========================
**YAML Path**       gitlab_url
**Key-Value Path**  gitlab_url
**Environment**     NOC_GITLAB_URL
**Default Value**   https://code.getnoc.com/
==================  ========================


.. _config-node:

node
~~~~

==================  ====================
**YAML Path**       node
**Key-Value Path**  node
**Environment**     NOC_NODE
**Default Value**   socket.gethostname()
==================  ====================


.. _config-pool:

pool
~~~~

==================  ==============================
**YAML Path**       pool
**Key-Value Path**  pool
**Environment**     NOC_POOL
**Default Value**   os.environ.get("NOC_POOL", "")
==================  ==============================


.. _config-secret_key:

secret_key
~~~~~~~~~~

==================  ==============
**YAML Path**       secret_key
**Key-Value Path**  secret_key
**Environment**     NOC_SECRET_KEY
**Default Value**   12345
==================  ==============


.. _config-timezone:

timezone
~~~~~~~~

==================  =============
**YAML Path**       timezone
**Key-Value Path**  timezone
**Environment**     NOC_TIMEZONE
**Default Value**   Europe/Moscow
==================  =============




