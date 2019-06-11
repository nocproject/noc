.. _dev-handlers-config-filter:

=====================
Config Filter Handler
=====================

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Interface for configuration filter. Configuration filters are
applied during Managed Object configuration save to GridVCS.
Config filters are used to alter configuration before further processing.
Altering may include any text manipulation, including section removing
and sensitive data protection.

Config filters are applied before :ref:`dev-handlers-config-diff-filter`.

.. function:: config_filter(managed_object, config)

    Implements config filter

    :param managed_object: Managed Object instance
    :param config: Config
    :returns: altered config

Examples
--------

Hide Passwords
^^^^^^^^^^^^^^
Replace *password <mypass>* with *password xxx*::

    import re

    rx_password = re.compile("password\s+(\S+)")

    def config_filter(mo, config):
        return rx_password.sub("xxx", rx_password)
