import os
import sys

from pyflakes import api
from pyflakes.checker import Checker
from pyflakes.reporter import Reporter

import cms
import menus


def _pyflakes_report_with_nopyflakes(self, messageClass, node, *args, **kwargs):
    with open(self.filename, 'r') as code:
        if code.readlines()[node.lineno - 1].strip().endswith('# nopyflakes'):
            return
    self.messages.append(messageClass(self.filename, node, *args, **kwargs))


def _pyflakes_no_migrations(self, tree, filename='(none)', builtins=None):
    if os.path.basename(os.path.dirname(filename)) in ('migrations',
                                                       'south_migrations'):
        self.messages = []
    else:
        Checker.___init___(self, tree, filename, builtins)


def _check_recursive(paths, reporter):
    """
    The builtin recursive checker tries to check .pyc files.
    """
    num_warnings = 0
    for path in api.iterSourceCode(paths):
        if path.endswith('.py'):
            num_warnings += api.checkPath(path, reporter)
    return num_warnings


def pyflakes():
    """
    Unfortunately, pyflakes does not have a way to suppress certain errors or
    a way to configure the checker class, so we have to monkey patch it.

    Returns number of warnings
    """
    Checker.___init___ = Checker.__init__
    Checker.__init__ = _pyflakes_no_migrations
    Checker.report = _pyflakes_report_with_nopyflakes
    reporter = Reporter(sys.stdout, sys.stderr)
    paths = [
        os.path.abspath(os.path.dirname(cms.__file__)),
        os.path.abspath(os.path.dirname(menus.__file__)),
        os.path.abspath(__file__),
    ]
    return _check_recursive(paths, reporter)
