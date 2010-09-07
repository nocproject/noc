.. _install_testing:

Testing
*******

Running test suite
==================

Once installed you can run NOC's test suite cycle to ensure installation and set up performed correctly.
PostgreSQL user ``noc`` must have permission to create database ``test_noc`` in order to run tests.
When all prerequisites met run::

    # su - noc
    $ cd /opt/noc
    $ python manage.py test

Built-in webserver
==================
You can quickly test web interface by running built-in webserver::

    # su - noc
    $ cd /opt/noc
    $ python manage.py runserver 0.0.0.0:8000

Builtin webserver is started at port 8000. Connect with your browser and enter
username and password set at :ref:`installation_init_database` step.
