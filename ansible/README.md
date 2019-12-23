# Ansible playbooks for NOC Tower

Primary goal of that playbook provide simple and very basic install of NOC.

Several notes that it will not do:
* remove external service from node (postgres, mongodb and so on) after disabling service in Tower
* backup your data, please do it by yourself
* move data from one host to another.

Thar repo should not intended to be used by itself. 
Use https://code.getnoc.com/noc/tower/blob/master/Readme.md instaed. 

# Additional roles

Want to use noc tower tu rule them all? you can check this group: https://code.getnoc.com/ansible-roles

# Supported platforms are:

* Debian 9
* Debian 10
* CentOS 7
* RHEL 7
* Ubuntu 16.04
* Ubuntu 18.04
* FreeBSD 12+

# Related work 

Be aware that this type of install get less love than current repo and can be not in best shape. 
Also be aware that each of them have some limitation. Read limitations sections carefully before apply.

* https://code.getnoc.com/noc/noc-dc -- want to install noc via docker compose and just sneak peak? That is the way.
* https://code.getnoc.com/noc/noc-k8s -- Already cloud native? Probably it will help you. 


