from __future__ import print_function
import pdb
import pytest


def find_test(currentframe):
    frame = currentframe
    while frame:
        for value in frame.f_locals.values():
            if isinstance(value, pytest.Item):
                return value
        frame = frame.f_back


class PdbExtension:
    def do_whichtest(self, arg):
        """whichtest
        Show which test we are currently in.
        """
        item = find_test(self.curframe)
        if item is None:
            print("Couldn't determine current test", file=self.stdout)
            return
        print("Currently in %s:%s: %s " % item.location, file=self.stdout)


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
