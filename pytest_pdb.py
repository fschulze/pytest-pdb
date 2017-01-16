from __future__ import print_function
import pdb
import pytest


def find_test(currentframe):
    frame = currentframe
    prev = frame
    while frame:
        for value in frame.f_locals.values():
            if isinstance(value, pytest.Item):
                return (value, prev)
        prev = frame
        frame = frame.f_back


class PdbExtension:
    def do_whichtest(self, arg):
        """whichtest
        Show which test we are currently in.
        """
        test = find_test(self.curframe)
        if test is None:
            print("Couldn't determine current test", file=self.stdout)
            return

        (item, frame) = test
        print("Currently in {} ({}:{}) on line {}".format(
            item.location[2], item.location[0], item.location[1] + 1,
            frame.f_lineno), file=self.stdout)


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
