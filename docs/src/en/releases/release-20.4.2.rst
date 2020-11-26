.. _release-20.4.2:

================
NOC 20.4.2
================

20.4.2 release contains `8 <https://code.getnoc.com/noc/noc/merge_requests?scope=all&state=merged&milestone_title=20.4.2>`_ bugfixes, optimisations and improvements.



.. _release-20.4.2-features:
New features
------------
Empty section



.. _release-20.4.2-improvements:
Improvements
------------
Empty section



.. _release-20.4.2-bugs:
Bugfixes
--------
+------------+-------------------------------------------------------------------------+
| MR         | Title                                                                   |
+------------+-------------------------------------------------------------------------+
| :mr:`4711` | noc/noc#1444 Fix trace get_confdb_query on empty ManagedObjectSelector. |
+------------+-------------------------------------------------------------------------+
| :mr:`4720` | Fix liftbridge alter                                                    |
+------------+-------------------------------------------------------------------------+
| :mr:`4729` | noc/noc#1449 Fix calculate lag_us metric on classifier.                 |
+------------+-------------------------------------------------------------------------+
| :mr:`4735` | Send reclassify event to liftbridge.                                    |
+------------+-------------------------------------------------------------------------+


.. _release-20.4.2-cleanup:
Code Cleanup
------------
Empty section



.. _release-20.4.2-profiles:
Profile Changes
---------------

.. _release-20.4.2-profile-DLink.DxS:
DLink.DxS
^^^^^^^^^
+------------+------------------------------------------------------------------+
| MR         | Title                                                            |
+------------+------------------------------------------------------------------+
| :mr:`4713` | DLink.DxS.get_metrics. Add 'Interface | Speed' metric to script. |
+------------+------------------------------------------------------------------+


.. _release-20.4.2-profile-MikroTik.RouterOS:
MikroTik.RouterOS
^^^^^^^^^^^^^^^^^
+------------+--------------------------------------+
| MR         | Title                                |
+------------+--------------------------------------+
| :mr:`4728` | MikroTik.RouterOS add cpu_usage.json |
+------------+--------------------------------------+


.. _release-20.4.2-collections:
Collections Changes
-------------------
+------------+----------------------------------------+
| MR         | Title                                  |
+------------+----------------------------------------+
| :mr:`4741` | Fyx typo 'desciption' -> 'description' |
+------------+----------------------------------------+


.. _release-20.4.2-deploy:
Deploy Changes
--------------
+------------+------------------------------------------------------------+
| MR         | Title                                                      |
+------------+------------------------------------------------------------+
| :mr:`4744` | Remove reload in liftbridge unit until proper pid handling |
+------------+------------------------------------------------------------+

