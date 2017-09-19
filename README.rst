pytest-pdb
==========

py.test plugin pytest plugin which adds pdb helper commands related to pytest.

Usage
-----

install via::

    pip install pytest-pdb

Commands
--------

``gototest | gt``
    When debugging with pdb, type ``gototest`` which brings you directly to
    the frame of the test function.


``whichtest | wt``
    When debugging with pdb, type ``whichtest`` which should print something like::

        Currently in test_pdb.py:13: TestClasses.test_class_pdb

    It works by walking the frame stack until it finds a test item in the locals.
    This depends on how ``pytest_pyfunc_call`` is implemented.
    If that changes or is replaced by a plugin, the whichtest command may fail.


``top``
     Move to top (oldest) frame.


``bottom``
     Move to bottom (newest) frame.


Changes
=======

0.3.0 - Unreleased
------------------

- Show offset of current frame to test frame.
  [blueyed, fschulze]

- Add ``top`` and ``bottom`` commands.
  [blueyed]

- Add ``wt``/``gt`` shortcuts.
  [blueyed]

- Add ``gototest`` command.
  [blueyed]

- Print location upon entering pdb.
  [blueyed, fschulze]


0.2.0 - 2017-01-17
------------------

- Fix/improve location reporting.
  [blueyed (Daniel Hahler)]


0.1.0 - 2016-07-09
------------------

- Initial release.
  [fschulze (Florian Schulze)]
