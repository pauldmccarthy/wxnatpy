#!/usr/bin/env python
#
# __init__.py - The wxnat package.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""The ``wxnat`` package provides the :class:`XNATBrowserPanel` class, a
``wxpython`` panel allowing a user to connect to and browse a XNAT repository.
"""


__version__ = '0.2.3'
"""The ``wxnat`` version number. """


from wxnat.browser import (XNATBrowserPanel,
                           XNATBrowserDialog,
                           XNATFileSelectEvent,
                           EVT_XNAT_FILE_SELECT_EVENT)
