SAE
===
Configuration
-------------
SAE configuration stored in etc/noc-sae.conf. Edit configuration file before starting SAE.

Running SAE
-----------
Daemon mode
^^^^^^^^^^^
By default SAE starts in daemon mode, detaches from terminal and continues execution in backgroung.
To run SAE::

    $ cd /opt/noc
    $ ./scripts/noc-sae.py start

Foreground mode
^^^^^^^^^^^^^^^
When started in foreground mode SAE do not detaches from terminal and enforces full debug output directed to current terminal.
To run SAE in foreground mode::

    $ cd /opt/noc
    $ ./scripts/noc-sae.py -f start

Stopping SAE
------------
To stop SAE run::

    $ cd /opt/noc
    $ ./scripts/noc-sae.py stop

