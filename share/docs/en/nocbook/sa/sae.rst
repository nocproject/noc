SAE
***

Configuration
=============
SAE configuration stored in etc/noc-sae.conf. Edit configuration file before starting SAE.

Running SAE
===========
From noc-launcher
-----------------
Set up etc/noc-launcher.conf::

    [noc-sae]
    enabled = true

to run SAE from noc-launcher

Daemon mode
-----------
To run SAE in daemon mode::

    $ cd /opt/noc
    $ ./scripts/noc-sae.py start

Foreground mode
---------------
When started in foreground mode SAE do not detaches from terminal and enforces full debug output directed to current terminal.
To run SAE in foreground mode::

    $ cd /opt/noc
    $ ./scripts/noc-sae.py -f start

Stopping SAE
============
To stop SAE, running in daemon mode::

    $ cd /opt/noc
    $ ./scripts/noc-sae.py stop

