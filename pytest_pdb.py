from __future__ import print_function
import pdb
import pytest


def find_test(stack):
    c = 0
    for st in stack:
        frame = st[0]
        c += 1
        if frame.f_code.co_name == 'pytest_pyfunc_call':
            if 'pyfuncitem' in frame.f_locals:
                item = frame.f_locals['pyfuncitem']
                if isinstance(item, pytest.Item):
                    return (item, stack[c][0], c)


class PdbExtension:
    def do_whichtest(self, arg):
        """whichtest
        Show which test we are currently in.
        """
        test = find_test(self.stack)
        if test is None:
            print("Couldn't determine current test.", file=self.stdout)
            return
        (item, frame, stack_idx) = test


        # Describe offset to current frame (for up/down).
        cur_idx = None
        for i, st in enumerate(self.stack, start=1):
            if st[0] == self.curframe:
                cur_idx = i
                break
        if cur_idx is None:
            print("warning: couldn't determine current frame.",
                  file=self.stdout)
        else:
            offset = stack_idx + 1 - cur_idx
            if offset == 0:
                desc = ' (at current frame)'
            elif offset > 0:
                desc = ' ({} frames down)'.format(offset)
            else:
                desc = ' ({} frames up)'.format(0 - offset)

        print("Currently in {} ({}:{}) on line {}{}.".format(
            item.location[2], item.location[0], item.location[1] + 1,
            frame.f_lineno, desc), file=self.stdout)

    def do_gototest(self, arg):
        """gototest
        Go to frame containing the test.
        """
        test_caller = find_test(self.stack)
        if test_caller is None:
            print("Couldn't determine current test.", file=self.stdout)
            return

        self._select_frame(test_caller[2])

    def do_top(self, arg):
        """top
        Move to top frame.
        """
        if self.curindex == 0:
            self.error('Oldest frame')
            return
        self._select_frame(0)

    def do_bottom(self, arg):
        """bottom
        Move to bottom frame.
        """
        if self.curindex + 1 == len(self.stack):
            self.error('Newest frame')
            return
        self._select_frame(len(self.stack) - 1)


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
