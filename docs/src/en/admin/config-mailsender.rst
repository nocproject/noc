.. _config-mailsender:

mailsender
----------


.. _config-mailsender-smtp_server:

smtp_server
~~~~~~~~~~~

==================  ==========================
**YAML Path**       mailsender.smtp_server
**Key-Value Path**  mailsender/smtp_server
**Environment**     NOC_MAILSENDER_SMTP_SERVER
**Default Value**   StringParameter()
==================  ==========================


.. _config-mailsender-smtp_port:

smtp_port
~~~~~~~~~

==================  ========================
**YAML Path**       mailsender.smtp_port
**Key-Value Path**  mailsender/smtp_port
**Environment**     NOC_MAILSENDER_SMTP_PORT
**Default Value**   25
==================  ========================


.. _config-mailsender-use_tls:

use_tls
~~~~~~~

==================  ======================
**YAML Path**       mailsender.use_tls
**Key-Value Path**  mailsender/use_tls
**Environment**     NOC_MAILSENDER_USE_TLS
**Default Value**   False
==================  ======================


.. _config-mailsender-helo_hostname:

helo_hostname
~~~~~~~~~~~~~

==================  ============================
**YAML Path**       mailsender.helo_hostname
**Key-Value Path**  mailsender/helo_hostname
**Environment**     NOC_MAILSENDER_HELO_HOSTNAME
**Default Value**   noc
==================  ============================


.. _config-mailsender-from_address:

from_address
~~~~~~~~~~~~

==================  ===========================
**YAML Path**       mailsender.from_address
**Key-Value Path**  mailsender/from_address
**Environment**     NOC_MAILSENDER_FROM_ADDRESS
**Default Value**   noc@example.com
==================  ===========================


.. _config-mailsender-smtp_user:

smtp_user
~~~~~~~~~

==================  ========================
**YAML Path**       mailsender.smtp_user
**Key-Value Path**  mailsender/smtp_user
**Environment**     NOC_MAILSENDER_SMTP_USER
**Default Value**   StringParameter()
==================  ========================


.. _config-mailsender-smtp_password:

smtp_password
~~~~~~~~~~~~~

==================  ============================
**YAML Path**       mailsender.smtp_password
**Key-Value Path**  mailsender/smtp_password
**Environment**     NOC_MAILSENDER_SMTP_PASSWORD
**Default Value**   SecretParameter()
==================  ============================


