#!/usr/bin/env python
#
# icons.py - Icons used by wxnat.browser.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module contains base-64 encoded icons used by the
:class:`.XNATBrowserPanel`. This is so that the ``wxnat`` library can be
easily embedded or frozen, without depending on having access to its icon
image files.
"""


import base64 as b64

from six import BytesIO, StringIO

import wx

import fsleyes_widgets as fwidgets


class IconError(Exception):
    """Custon ``Exception`` raised when :func:`loadBitmap` cannot load
    an icon.
    """
    pass


def loadBitmap(iconb64):
    """Convert the given ``base64``-encoded byte string to a ``wx.Bitmap``
    object.
    """

    iconbytes = b64.b64decode(iconb64)
    success   = False

    if fwidgets.wxversion() == fwidgets.WX_PHOENIX:
        image   = wx.Image()
        success = wx.Image.LoadFile(image, BytesIO(iconbytes))
    else:
        image   = wx.EmptyImage()
        success = wx.Image.LoadStream(image, StringIO(iconbytes))

    if not success:
        raise IconError('Error loading icon')

    return image.ConvertToBitmap()


FILE_ICON = b'''
iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA/wD/AP+gvaeTAAAACXBI
WXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH4QoUDRcmW1Eo1gAAACZpVFh0Q29tbWVudAAAAAAAQ3Jl
YXRlZCB3aXRoIEdJTVAgb24gYSBNYWOV5F9bAAAA8klEQVQ4y5XSvUoEQRAE4O92VcRAIwUTRQNR
xMTQF5EL9Q3F8DA1UfANRDTQUBTOP27WpMFh2B21YZihlq6tri5+qlWvpgY2WEE3cL6Q+n4yF/cI
G/G+xEM0whSncS8FyawkanEYTceF3Aab8W1ajtMMjJVLTXjEFhbwFNiwMYHPZyfhDldY7POgrD1s
hzcdXjEJsuY3goQd7GcE70FgaAul/DOcZ1g3FI4+glGsaz1rfsH9XwlmOMFRbCPhDeNaTPMcjGNd
pSq4DjXVfH/gs8C6zOBe5hYHuMEtnnuMS9iN93LpQRf5hzWsVsa9qPnw7/oGgkQ4BdavorgAAAAA
SUVORK5CYII='''.strip().replace(b'\n', b'')
"""Icon used in the ``XNATBrowserPanel`` for files. """


FOLDER_LOADED_ICON = b'''
iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA/wD/AP+gvaeTAAAACXBI
WXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH4QoUDRYElypYcwAAACZpVFh0Q29tbWVudAAAAAAAQ3Jl
YXRlZCB3aXRoIEdJTVAgb24gYSBNYWOV5F9bAAAAv0lEQVQ4y8XTO27CQBCA4c+WHQkplPRcIAWX
S65CQZkCcQDOQIVExylSIFkxYMdp1siyFtkJBSNNsfP4d2Z2lgcl6Z03mCONxK2wRBMDveADVxQ4
9bQKia8RuCQYG5R3Kp0G/75jSyELjk+cQ8AGdQ9Q4QsLrDs52zbgOxjHaomDTj8X7EI7Y/Qc5nUD
JMj/83rpo3vwfEAW6WsI+jMEmAwAihggwdu9PY9I2V7YAt4x+8NMahy7ZeeRn2nELKpfEzQzZl5l
tM8AAAAASUVORK5CYII='''.strip().replace(b'\n', b'')
"""Icon used in the ``XNATBrowserPanel`` for folders, the contents of
which have been downloaded from the XNAT server.
"""


FOLDER_UNLOADED_ICON = b'''
iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA/wD/AP+gvaeTAAAACXBI
WXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH4QoUDRYbGiJVhgAAACZpVFh0Q29tbWVudAAAAAAAQ3Jl
YXRlZCB3aXRoIEdJTVAgb24gYSBNYWOV5F9bAAAAwklEQVQ4y8XSPWpCQRQF4O89NQQbC0mVMqC4
ANdgJ27BJVgIWY8bcQkiKKnSi5DK0t9mhGF4L4yxyGmGOXfmzDl3Lk+iSPYTdCp4WGOVks2wNjBE
D2dck3MtjLDFsaKuwCfmNU5fQn2aur9bHaOPHQ4VL1zwgVd8BW6D73uEXojxntG3QYjZjQXO2GOR
2fxZcKWM8pR/+b3y2Tn4f4FmxnSmuNYJFL+IxjjWCbyFacvBKRVYop1hP47xE9suH7gci1xuwmof
AMglWYsAAAAASUVORK5CYII='''.strip().replace(b'\n', b'')
"""Icon used in the ``XNATBrowserPanel`` for folders, the contents of
which have not yet been downloaded from the XNAT server.
"""
