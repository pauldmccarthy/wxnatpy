#!/usr/bin/env python
#
# __init__.py - The wxnat package.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""The ``wxnat`` package provides the :class:`XNATBrowserPanel` class, a
``wxpython`` panel allowing a user to connect to and browse a XNAT repository.
"""


import os.path as op

from wxnat.browser import (XNATBrowserPanel,
                           XNATBrowserDialog,
                           XNATFileSelectEvent,
                           XNATItemHighlightEvent,
                           EVT_XNAT_FILE_SELECT_EVENT,
                           EVT_XNAT_ITEM_HIGHLIGHT_EVENT)


__version__ = '0.4.0'
"""The ``wxnat`` version number. """


def generateFilePath(fobj):
    """Generate a file/directory path for the given ``xnat.FileData``
    object. The generated path can be used as a unique destination when
    downloading a file.

    The generated path has the form::

        <project>/<subject>/<experiment>/<scan>/<resource>/<filename>
    """

    # We generate the path by taking the file object URI (it's
    # unique identifier on the XNAT server), and stripping of
    # the XNAT hierarchy level identifiers. This feels a bit
    # hacky, but there is no other way to identify where a
    # given FileData object resides in the hierarchy (as they
    # don't seem to preserve a reference to their parent node).
    remove = ['/data',
              '/projects',
              '/subjects',
              '/experiments',
              '/assessors',
              '/scans',
              '/resources',
              '/files']

    path = fobj.uri

    for rem in remove:
        path = path.replace(rem, '')

    path = path.lstrip('/').split('/')

    return op.join(*path)
