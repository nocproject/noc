Activators
==========
* **Name** - Activator name. Used for authentication. Must match with [activator]/name in noc-activator.conf
* **IP** - Source IP address seen by SAE. May be one of activator's interfaces or NAT pool if on the way. SAE forcefully refuses connection from unknown addresses.
* **Auth string** - Secret used for authentication. Must match with [activator]/secret in noc-activator.conf
* **Is Active** - Can activator authenticate now. Set checkbox when activator can authenticate, or uncheck to temporary disable following authentication attempts. Changing **Is Active** does not follow immediately activator connect/disconnect.
