#!/usr/bin/env python
##
##
##

##
## Use setuptools instead of docutils
##
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

setup(name='noc',
      version='0.1',
      description='Network Operation Center\'s OSS',
      author='Dmitry Volodin',
      author_email='dv@noc.effortel.ru',
      url='<nothing yet>',
      zip_safe=False,
      packages=find_packages(),
      install_requires=[
        "psycopg2",
        "Django >= 1.0",
        #"south"
        "flup >= 1.0",
        "Sphinx >= 0.4",
      ],
      dependency_links = [
        ""
      ],
     )
