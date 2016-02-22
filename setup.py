#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

Version = '0.1.1'
setup(name='django-admin-ip-whitelist',
      version=Version,
      # install_requires='redis',
      description="Django middleware to allow access to /admin only for users, whose IPs are in the white list",
      long_description="django-admin-ip-whitelist is a django middleware app to allow access to /admin by IP addresses",
      author="dvska",
      url="http://github.com/dvska/django-admin-ip-whitelist",
      packages=['admin_ip_whitelist'],
      license='Apache',
      platforms='Posix; MacOS X;',
      classifiers=[
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          'Topic :: Internet :: WWW/HTTP',
          'Topic :: Software Development :: Libraries :: Application Frameworks',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
     )
