.. _OS.FreeBSD:

OS.FreeBSD
===========

====== =====================================
Vendor `FreeBSD <http://www.freebsd.org/>`_
OS     FreeBSD
====== =====================================

OS.FreeBSD profile supports software FreeBSD-based routers

Important
---------
Preparation of user account working together with NOC:

* Use native shells (sh, csh) or manually set prompt to compatible with their syntax
* Put '.hushlogin' file into user directory
* Disable 'fortune' and other stuff
* If you don't want to invite user into 'wheel' group, use alias(1) to invoke 'sudo'
* Do not use localized-message user class

Tested Equipment
----------------
.. supported:: OS.FreeBSD
