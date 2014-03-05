import os
import sys

from setuptools import setup, find_packages


setup(name="flatland0",
      version='0.0.1.dev1',
      author='Jason Kirtland',
      author_email='jek@discorporate.us',
      description='HTML form management and validation',
      keywords='schema validation data web form forms roundtrip',
      long_description=open('README.rst').read(),
      license='MIT License',
      url='https://github.com/mbr/flatland0',
      packages=find_packages(exclude=['tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'blinker', 'six',
          ],
      )
