flatland0
=========

.. image:: https://travis-ci.org/mbr/flatland0.png?branch=master
   :target: https://travis-ci.org/mbr/flatland0

Flatland maps between rich, structured Python application data and the
string-oriented flat namespace of web forms, key/value stores, text
files and user input.  Flatland provides a schema-driven mapping
toolkit with optional data validation.

Flatland is great for:

  - Collecting, validating, re-displaying and processing HTML form
    data

  - Dealing with rich structures (lists, dicts, lists of dicts, etc.)
    in web data

  - Validating JSON, YAML, and other structured formats

  - Associating arbitrary Python types with JSON, .ini, or sys.argv
    members that would otherwise deserialize as simple strings.

  - Reusing a single data schema for HTML, JSON apis, RPC, ...

The core of the flatland toolkit is a flexible and extensible
declarative schema system representing many data types and structures.

A validation system and library of schema-aware validators is also
provided, with rich i18n capabilities for use in HTML, network APIs
and other environments where user-facing messaging is required.


Forked from flatland
--------------------

flatland0 is a fork of `flatland <https://pypi.python.org/pypi/flatland>`_
written by Jason Kirtland and currently under development.

There is currently ongoing work of porting all test cases from nose to py.test
to simplify their structure and get working Python3 support based on that.
Currently, 675/716 test cases are run on Python3 and the library is usable,
but should be considered beta quality when not running on Python2.
