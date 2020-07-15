==========================================
Sharing collections from NOC web interface
==========================================

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

First of all NOC is an open-source product, so we want to give easy way
to share your collection models with the community.

So, you have a self-made collection, for example a new model of switch or connection rule or etc.

1. Register at our `Repository <https://code.getnoc.com>`_

2. Create a `Personal Access Token <https://code.getnoc.com/profile/personal_access_tokens>`_ with `api` Scope checked.
Remember it!

3. Open a model, that you want to share in NOC web interface, for example:

.. image:: /images/howto_share_json.png

4. Use the Force, Luke, and fill up all the forms.

.. image:: /images/howto_share_json2.png

.. image:: /images/howto_share_apikey.png

.. image:: /images/howto_share_descr.png

5. Then NOC will send file(your browser should have access to the Internet) to the repository and opens a Merge Request.
Some browsers will prevent open a new popup, so check this moment.

.. image:: /images/howto_share_mr.png

6. Congratulations with your contribution and thank you.


N.B.
In case if you forgot your token or you want to change it:

.. code-block:: python

    ./noc shell
    from noc.core.mongo.connection import connect
    connect()
    from noc.main.models.apitoken import APIToken
    from noc.aaa.models.user import User
    user = User.objects.get(username="YOUR_NOC_LOGIN")
    token = APIToken.objects.filter(type="noc-gitlab-api", user=user.id).first()
    token.token = "NEW_TOKEN"
    token.save()

