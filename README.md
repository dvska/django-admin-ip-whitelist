django-admin-ip-whitelist
====
django-admin-ip-whitelist is a Django middleware app to ban users whose IPs are not whitelisted.

Stores whole 'whitelist' in memory to avoid database lookups on every request. 


Installation
------------

Requirements:

* Python 2.5+
* Django
* Memcache/Redis/.. 

Get django-admin-ip-whitelist 
--------

Get the source:

Browse the source on GitHub: <http://github.com/dvska/django-admin-ip-whitelist>

Clone with Git:

    $ git clone git://github.com/dvska/django-admin-ip-whitelist


Install via easy_install or pip

    easy_install django-admin-ip-whitelist
    pip install django-admin-ip-whitelist


Setup
------
Install django-admin-ip-whitelist. Make sure it is on your PYTHONPATH or in your django project directory.

In your django project settings.py you must set the following options:

    1) Add 'admin_ip_whitelist.middleware.AdminAccessIPWhiteListMiddleware' to MIDDLEWARE_CLASSES

    2) Add 'admin_ip_whitelist' to INSTALLED_APPS

    3) Add ADMIN_ACCESS_WHITELIST_ENABLED = True to enable django-admin-ip-whitelis (handy if you lock yourself out, you can just set this to False)

    4) Run migrations to create the table for whitelisted IPs:

        ./manage.py migrate admin_ip_whitelist

    4) Optionally set ADMIN_ACCESS_WHITELIST_MESSAGE (default is "You are banned.") to change default message for banned user.

Issues
------
Find a bug? Want a feature? Submit an [issue
here](http://github.com/dvska/django-admin-ip-whitelist/issues). Patches welcome!

License
------
django-admin-ip-whitelist is released under the Apache Software License, Version 2.0


Authors
-------
 * dvska
