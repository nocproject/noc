*************
Configuration
*************

Create Database
===============
Create database user ``noc`` from PostgreSQL superuser (``pgsql`` in example)::

    # su - pgsql
    pgsql@/$ createuser noc
    Shall the new role be a superuser? (y/n) n
    Shall the new role be allowed to create databases? (y/n) n
    Shall the new role be allowed to create more new roles? (y/n) n

Then create database ``noc`` owned by user ``noc``::
    
    $ createdb -EUTF8 -Onoc noc
    
Configuration Files
===================
Set up *etc/noc.conf:[database]* section.

.. _Initialize-Database:

Initialize Database
===================
Initialize database, Fault Management rules and online documentation by::

    # su - noc
    noc@/$ cd /opt/noc
    noc@/opt/noc$ ./scripts/post-update

During intialization you will be prompted to create first NOC database superuser.
Enter superuser's name, password and email.
