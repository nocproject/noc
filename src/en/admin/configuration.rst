====================
Configuration System
====================

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 2
    :class: singlecol

NOC configuration system is the flexible tool to load, combine
and override configuration on per-process basis.

.. _noc_config:

NOC_CONFIG
----------
Config sources and their preference are defined in *NOC_CONFIG*
environment variable. *NOC_CONFIG* contains comma-separated list of source URLs.
Sources are loaded and processed in enumerated order.
Refer to :ref:`admin-configuration-sources` section for full list of possible
sources and their configuration.

Each source may provide couple of configuration variables. During loading
each configuration variable provided by source overrides previously
loaded one. So variables are processed in LIFO order, where last
definition wins. This allows to combine configuration from different
parts according to desired policy.

Default value for *NOC_CONFIG*::

    NOC_CONFIG=legacy:///,yaml:///opt/noc/etc/settings.yml,env:///NOC

Which means:

#. Load legacy config "noc.yml" if exist (See :ref:`admin-configuration-sources-legacy` for details)
#. Load new YAML config from "settings.yml", provisioned by *Tower* (See :ref:`admin-configuration-sources-yaml` for details)
#. Apply NOC_xxx environment variables passed to process (See :ref:`admin-configuration-sources-env` for details)

Proposed approach allows to start with legacy config, if exists, override
it with *Tower* config and, finally, apply per-process tweaks via
environment variables.

You can set own *NOC_CONFIG* environment variable passed to process
to apply custom configuration processing order.

.. note::

    Configuration is loaded once on NOC's processes start.
    NOC doesn't track configuration changes.
    Restart appropriate services to apply configuration changes.

.. _admin-configuration-sources:

Sources
-------

.. _admin-configuration-sources-yaml:

yaml
^^^^
*Tower* YAML format

URL format::

    yaml://<path>

where *<path>* is YAML file absolute path.

Example::

    yaml:///opt/noc/etc/settings.yml

.. note::

    First two slashes after colon belongs to schema delimiter, while
    third slash is a root directory

"settings.yml" file usually deployed by *Tower*.
*yaml* source yields empty config if file is not found or not accessible.

See :ref:`admin-config` for possible configuration variable names.
i.e. *web.language* written in YAML as::

    web:
        language: en

.. _admin-configuration-sources-env:

env
^^^
Load configuration from environment variables. Best used to finally
alter configuration for particular process.

URL format::

    env:///<prefix>

Where *<prefix>* is prefix of configuration variable.

Example. Try to load environment variables started with *NOC_*::

    env:///NOC

Then following environment will be processed as:

========================== =============================================
Environment                Configuration
========================== =============================================
NOC_FEATURE_UVLOOP=1       feature.uvloop=True
NOC_TIMEZONE=Europe/Moscow timezone=Europe/Moscow
NOC_FOOBAR                 *ignored*
MYVAR_FEATURE_UVLOOP=1     *ignored*
========================== =============================================

If we'll change URL to::

    env:///MYVAR

Then previous example will be processed as:

========================== =============================================
Environment                Configuration
========================== =============================================
NOC_FEATURE_UVLOOP=1       *ignored*
NOC_TIMEZONE=Europe/Moscow *ignored*
NOC_FOOBAR                 *ignored*
MYVAR_FEATURE_UVLOOP=1     feature.uvloop=True
========================== =============================================

.. note::

    See :ref:`admin-config` for possible environment variable names.
    Note that names given considered *NOC* prefix

.. _admin-configuration-sources-consul:

consul
^^^^^^
Load config from `Consul <https://www.consul.io>`_ distributed key-value
storage.

URL format::

    consul://<ip1>:<port>/<path>?token=<token>

Where:
* *<ip1>*: IP address or host name of *Consul* node
* *<port>*: Consul port
* *<path>*: Key-Value store prefix
* *<token>*: Consul access *token*, if exists

Example::

    consul://consul:8500/noc

Single *Consul* cluster can be used for several *consul* sources
using different *<path>*.

Example::

    NOC_CONFIG=consul://consul:8500/noc/global,consul://consul:8500/noc/dc/DC1

Example suggest global configuration is stored in "noc/global" tree,
datacenter-specific configurations are in "noc/dc" ("noc/dc/DC1" for "DC1").

Get current value for *consul* key::

    $ consul kv get -recurse noc/language
    noc/language:ru

Change *consul* key::

    $ consul kv put noc/language en
    Success! Data written to: noc/language
    $ consul kv get -recurse noc/language
    noc/language:en

Dump all consul config::

    /opt/noc$ NOC_CONFIG=consul://consul:8500/noc ./noc config dump

.. _admin-configuration-sources-legacy:

legacy
^^^^^^
Legacy YAML format. Used for transitional purposes only.

URL format::

    legacy://<path>

where *<path>* is YAML file absolute path.

Examples::

    legacy:///
    legacy:///opt/noc/etc/noc.yml


.. note::

    First two slashes after colon belongs to schema delimiter, while
    third slash is a root directory

"noc.yml" file usually deployed by older versions of *Tower*.
*legacy* source yield empty config if file is not found or not accessible.

*legacy* config may be converted to *yaml*::

    /opt/noc# NOC_CONFIG=legacy:/// ./noc config dump > etc/settings.yml

