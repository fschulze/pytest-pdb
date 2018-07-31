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


def find_settrace_frame(curframe):
    frame = curframe
    while frame:
        if frame.f_code.co_name == 'set_trace':
            if frame.f_back:
                return frame.f_back
        frame = frame.f_back


def offset_between_frames(currentframe, destinationframe):
    # search from current
    index = 0
    frame = currentframe
    while frame:
        if frame == destinationframe:
            return index
        index -= 1
        frame = frame.f_back
    # search from destination
    index = 0
    frame = destinationframe
    while frame:
        if frame == currentframe:
            return index
        index += 1
        frame = frame.f_back


def offset_description(offset):
    if offset == 0:
        return 'at current frame'
    elif offset == 1:
        return '1 frame above'
    elif offset > 1:
        return '%s frames above' % offset
    elif offset == -1:
        return '1 frame below'
    else:
        return '%s frames below' % -offset


class PdbExtension:
    def do_whichtest(self, arg):
        """whichtest | wt
        Show which test we are currently in.
        """
        (test, frame, index) = find_test_by_stack(self.stack)
        if test is None:
            print("Couldn't determine current test", file=self.stdout)
            return

        offset = index - self.curindex

        print("Currently in {} ({}:{}) on line {} ({})".format(
            test.location[2], test.location[0], test.location[1] + 1,
            frame.f_lineno, offset_description(offset)), file=self.stdout)
    do_wt = do_whichtest

    def do_gototest(self, arg):
        """gototest | gt
        Go to frame containing the test.
        """
        (test, frame, index) = find_test_by_stack(self.stack)
        if test is None:
            print("Couldn't determine current test.", file=self.stdout)
            return

        self._select_frame(index)
    do_gt = do_gototest

    def do_top(self, arg):
        """top
        Move to top (oldest) frame.
        """
        if self.curindex == 0:
            self.error('Oldest frame')
            return
        self._select_frame(0)

    def do_bottom(self, arg):
        """bottom
        Move to bottom (newest) frame.
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
            setattr(
                PdbExtension,
                'help_%s' % cmd,
                lambda self: print(doc, file=self.stdout))

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
    curframe = sys._getframe().f_back
    (test, frame) = find_test_by_frame(curframe)
    if test is None:
        tw.sep(">", "Couldn't determine current test")
        return

    offset = offset_between_frames(find_settrace_frame(curframe), frame)
    desc = ''
    if offset is not None:
        desc = ' (%s)' % offset_description(offset)

    tw.sep(">", "Currently in {} ({}:{}) on line {}{}".format(
        test.location[2], test.location[0], test.location[1] + 1,
        frame.f_lineno, desc))
