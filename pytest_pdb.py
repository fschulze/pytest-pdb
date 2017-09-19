from __future__ import print_function
import pdb
import pytest
import sys


def find_test_by_frame(currentframe):
    frame = currentframe
    prev = frame
    while frame:
        for value in frame.f_locals.values():
            if isinstance(value, pytest.Item):
                return (value, prev)
        prev = frame
        frame = frame.f_back
    return (None, currentframe)


def find_test_by_stack(stack):
    for index, (frame, lineno) in reversed(list(enumerate(stack))):
        for value in frame.f_locals.values():
            if isinstance(value, pytest.Item):
                return (value, stack[index + 1][0], index + 1)
    return (None, stack[0], 0)


class PdbExtension:
    def do_whichtest(self, arg):
        """whichtest
        Show which test we are currently in.
        """
        (test, frame, index) = find_test_by_stack(self.stack)
        if test is None:
            print("Couldn't determine current test", file=self.stdout)
            return

        print("Currently in {} ({}:{}) on line {}".format(
            test.location[2], test.location[0], test.location[1] + 1,
            frame.f_lineno), file=self.stdout)

    def do_gototest(self, arg):
        """gototest
        Go to frame containing the test.
        """
        (test, frame, index) = find_test_by_stack(self.stack)
        if test is None:
            print("Couldn't determine current test.", file=self.stdout)
            return

        self._select_frame(index)


def pytest_configure(config):
    cmds = {x[3:] for x in dir(PdbExtension) if x.startswith('do_')}
    # setup help_* for Python 2.x
    for cmd in cmds:
        doc = getattr(
            getattr(PdbExtension, 'do_%s' % cmd), '__doc__', None)
        if doc:
            setattr(PdbExtension, 'help_%s' % cmd, lambda self: print(doc, file=self.stdout))

    prefixes = {'do', 'help'}
    for prefix in prefixes:
        for cmd in cmds:
            attr = '%s_%s' % (prefix, cmd)
            if hasattr(pdb.Pdb, attr):
                raise ValueError
    for prefix in prefixes:
        for cmd in cmds:
            attr = '%s_%s' % (prefix, cmd)
            if hasattr(PdbExtension, attr):
                setattr(pdb.Pdb, attr, getattr(PdbExtension, attr))


def pytest_enter_pdb(config):
    import _pytest.config
    tw = _pytest.config.create_terminal_writer(config)
    (test, frame) = find_test_by_frame(sys._getframe().f_back)
    if test is None:
        tw.sep(">", "Couldn't determine current test")
        return

    tw.sep(">", "Currently in {} ({}:{}) on line {}".format(
        test.location[2], test.location[0], test.location[1] + 1,
        frame.f_lineno))
