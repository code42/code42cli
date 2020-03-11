"""
This module handles import compatibility issues between Python 2 and
Python 3.
"""
# pylint: disable=undefined-variable,import-error,unused-import,no-name-in-module

import sys

_ver = sys.version_info

#: Python 2.x?
is_py2 = _ver[0] == 2

if is_py2:
    from urlparse import urljoin, urlparse

    str = unicode

    import repr as reprlib
else:
    from urllib.parse import urljoin, urlparse

    str = str

    import reprlib
