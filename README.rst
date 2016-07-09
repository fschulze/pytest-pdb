pytest-pdb
==========

py.test plugin pytest plugin which adds pdb helper commands related to pytest.

Usage
-----

install via::

    pip install pytest-pdb

Commands
--------

``whichtest``

    When debugging with pdb, type ``whichtest`` which should print something like::

        Currently in test_pdb.py:13: TestClasses.test_class_pdb

    It works by walking the frame stack until it finds a test item in the locals.
    This depends on how ``pytest_pyfunc_call`` is implemented.
    If that changes or is replaced by a plugin, the whichtest command may fail.


Changes
=======

0.1.0 - Unreleased
------------------

- Initial release.
  [fschulze (Florian Schulze)]
