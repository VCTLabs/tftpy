# vim: ts=4 sw=4 et ai:
"""
This library implements the tftp protocol, based on rfc 1350.
http://www.faqs.org/rfcs/rfc1350.html
At the moment it implements only a client class, but will include a server,
with support for variable block sizes.

As a client of tftpy, this is the only module that you should need to import
directly. The TftpClient and TftpServer classes can be reached through it.
"""

import sys

from . import TftpContexts, TftpPacketFactory, TftpPacketTypes, TftpStates
from .TftpClient import TftpClient
from .TftpServer import TftpServer
from .TftpShared import *

if sys.version_info < (3, 8):
    from importlib_metadata import version, PackageNotFoundError
else:
    from importlib.metadata import version, PackageNotFoundError


# Make sure that this is at least Python 3
required_version = (3, 0)
if sys.version_info < required_version:
    raise ImportError("Requires at least Python 3.0")


def _get_version():
    try:
        pkg_version = version("tftpy")
    except PackageNotFoundError:
        pkg_version = None
    return pkg_version


__version__ = _get_version()
