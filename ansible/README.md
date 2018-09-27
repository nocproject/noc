Ansible playbooks for NOC Tower

Primary goal of that playbook provide simple install of NOC.

Several notes that it will not do:
* remove external service from node (postgres, mongodb and so on) after disabling service in Tower
* backup your data, please do it by yourself
* move data from one host to another.

Supported platforms are:

* Debian 8
* Debian 9
* CentOS 7
* RHEL 7
* Ubuntu 16.04
* Ubuntu 18.04
* FreeBSD 11+

