Periodic Tasks
**************
SAE supports concept of periodic tasks. Periodic tasks are code snippets repeatedly executed every given interval of time.
Periodic tasks are similar to UNIX traditional ''cron'' though some differences are present:

* periodic tasks executed in context of SAE process in separate threads
* periodic tasks share common database connection pool
* periodic tasks are python modules residing in ''periodics'' directory of the NOC modules
* periodic tasks are the part of NOC modules itself
* periodic tasks have access to SAE internals
