*******************
Solaris 10 Specific
*******************

SMF
===
All major NOC processes can be run via SMF framework.
Manifests can be found at share/sunos/manifest/.

Import manifests first (if not imported by installer)::

    $ svccfg import /opt/noc/share/sunos/manifest/noc-fcgi.xml
    $ svccfg import /opt/noc/share/sunos/manifest/noc-sae.xml
    $ svccfg import /opt/noc/share/sunos/manifest/noc-activator.xml
    $ svccfg import /opt/noc/share/sunos/manifest/noc-classifier.xml

Then you can start service (noc-fcgi, noc-sae, noc-activator and noc-classifier)::

    $ svcadm enable <service>

or stop service::

    $ svcadm disable <service>

at any time.

Check all noc services are healthy by::

    $ svcs -vx

