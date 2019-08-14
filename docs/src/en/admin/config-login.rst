.. _config-login:

login
-----


.. _config-login-methods:

methods
~~~~~~~

==================  =================
**YAML Path**       login.methods
**Key-Value Path**  login/methods
**Environment**     NOC_LOGIN_METHODS
**Default Value**   local
==================  =================


.. _config-login-session_ttl:

session_ttl
~~~~~~~~~~~

==================  =====================
**YAML Path**       login.session_ttl
**Key-Value Path**  login/session_ttl
**Environment**     NOC_LOGIN_SESSION_TTL
**Default Value**   7d
==================  =====================


.. _config-login-language:

language
~~~~~~~~

==================  ==================
**YAML Path**       login.language
**Key-Value Path**  login/language
**Environment**     NOC_LOGIN_LANGUAGE
**Default Value**   en
==================  ==================


.. _config-login-restrict_to_group:

restrict_to_group
~~~~~~~~~~~~~~~~~

==================  ===========================
**YAML Path**       login.restrict_to_group
**Key-Value Path**  login/restrict_to_group
**Environment**     NOC_LOGIN_RESTRICT_TO_GROUP
**Default Value**
==================  ===========================


.. _config-login-single_session_group:

single_session_group
~~~~~~~~~~~~~~~~~~~~

==================  ==============================
**YAML Path**       login.single_session_group
**Key-Value Path**  login/single_session_group
**Environment**     NOC_LOGIN_SINGLE_SESSION_GROUP
**Default Value**
==================  ==============================


.. _config-login-mutual_exclusive_group:

mutual_exclusive_group
~~~~~~~~~~~~~~~~~~~~~~

==================  ================================
**YAML Path**       login.mutual_exclusive_group
**Key-Value Path**  login/mutual_exclusive_group
**Environment**     NOC_LOGIN_MUTUAL_EXCLUSIVE_GROUP
**Default Value**
==================  ================================


.. _config-login-idle_timeout:

idle_timeout
~~~~~~~~~~~~

==================  ======================
**YAML Path**       login.idle_timeout
**Key-Value Path**  login/idle_timeout
**Environment**     NOC_LOGIN_IDLE_TIMEOUT
**Default Value**   1w
==================  ======================


.. _config-login-pam_service:

pam_service
~~~~~~~~~~~

==================  =====================
**YAML Path**       login.pam_service
**Key-Value Path**  login/pam_service
**Environment**     NOC_LOGIN_PAM_SERVICE
**Default Value**   noc
==================  =====================


.. _config-login-radius_secret:

radius_secret
~~~~~~~~~~~~~

==================  =======================
**YAML Path**       login.radius_secret
**Key-Value Path**  login/radius_secret
**Environment**     NOC_LOGIN_RADIUS_SECRET
**Default Value**   noc
==================  =======================


.. _config-login-radius_server:

radius_server
~~~~~~~~~~~~~

==================  =======================
**YAML Path**       login.radius_server
**Key-Value Path**  login/radius_server
**Environment**     NOC_LOGIN_RADIUS_SERVER
**Default Value**   StringParameter()
==================  =======================


.. _config-login-user_cookie_ttl:

user_cookie_ttl
~~~~~~~~~~~~~~~

==================  =========================
**YAML Path**       login.user_cookie_ttl
**Key-Value Path**  login/user_cookie_ttl
**Environment**     NOC_LOGIN_USER_COOKIE_TTL
**Default Value**   1
==================  =========================

.. _config-login-register_last_login:

register_last_login
~~~~~~~~~~~~~~~~~~~

==================  =============================
**YAML Path**       login.register_last_login
**Key-Value Path**  login/register_last_login
**Environment**     NOC_LOGIN_REGISTER_LAST_LOGIN
**Default Value**   True
==================  =============================

Write each successful login into User's last_login field
