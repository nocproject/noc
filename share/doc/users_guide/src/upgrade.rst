#######
Upgrade
#######

-------
Warning
-------
It is strongly neccessary to back up noc database
before upgrade:

::
    pg_dump -U noc noc > noc.dump

---------------------
Getting A New Version
---------------------

::
    cd <nocroot>
    hg pull
    hg update

------------------
Migrating database
------------------

::
    cd <nocroot>
    python manage.py migrate


