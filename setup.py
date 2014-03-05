import os
import sys

from setuptools import setup, find_packages

long_desc = open('README').read()

setup(name="flatland0",
      version='0.0.1.dev1',
      packages=find_packages(exclude=['tests.*', 'tests']),
      author='Jason Kirtland',
      author_email='jek@discorporate.us',
      description='HTML form management and validation',
      keywords='schema validation data web form forms roundtrip',
      long_description=long_desc,
      license='MIT License',
      url='https://github.com/mbr/flatland0',
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'blinker', 'six',
          ],
      **extra_setup)
