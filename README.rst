====
temp
====


.. image:: https://img.shields.io/pypi/v/temp.svg
        :target: https://pypi.python.org/pypi/temp

.. image:: https://img.shields.io/travis/rhangelxs/temp.svg
        :target: https://travis-ci.org/rhangelxs/temp

.. image:: https://readthedocs.org/projects/temp/badge/?version=latest
        :target: https://temp.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


.. image:: https://pyup.io/repos/github/rhangelxs/temp/shield.svg
     :target: https://pyup.io/repos/github/rhangelxs/temp/
     :alt: Updates



Python Boilerplate contains all the boilerplate you need to create a Python package.


* Free software: MIT license
* Documentation: https://temp.readthedocs.io.


Features
--------

* TODO

Quickstart
________

## Install requirements

pip install -r requirements_dev.txt

## Running tests with makefile

Remove previous results of tests: `make clean`

- Quick using pytests: `make test`

- Full using tox: `make test-all`

- Code coverage: `make coverage`

Documentation
________

Why we can't use DB with proper wrapper?
If so -> let's storing everything in-memory. Let's imagine we rewrite AMPQ.

Sets are hashable in Python and fast.

## Storage class
It is stupid, but should be database-like, it can be extended to support save and load state.

## Not parallel
Working in one thread :(
But without race condition.

## Tests
Tests have good coverage (in Python 2.7 and 3.6) using tox and py.test

## Itertools manual: [https://pymotw.com/3/itertools/]

## Restrictions by design

* Users can't follow themselves
* Anonymous posts not allowed
* CLI interface still not available

## High-level design
The idea was make it in MVC pattern, but splitting model and controller in this ad-hoc design will have overhead.

K << Total number of messages (M)

Followers << K

Followers << Users (U)

## Performance

BigO notation not the case.

But some overview:
 - Messages stored in chunks by authors and connected authors (can be shared in cluster).
 - Writing a message is slow (need as least two checks, in worst case will be U + M)
 - Generation of timeline takes about two-to-tree times up to follower messages and later strip to K limit.



Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
