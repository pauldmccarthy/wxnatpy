#!/usr/bin/env python
#
# test_start_end.py - Tests starting/ending sessions
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import time

import wx

from . import run_with_wx, yield_until

from wxnat import XNATBrowserPanel


def test_start_end():
    run_with_wx(_test_start_end)
def _test_start_end():

    parent = wx.GetTopLevelWindows()[0]
    panel  = XNATBrowserPanel(parent)
    result = [None]

    def callback(val):
        result[0] = val

    panel.StartSession('not.a.xnat.server',
                       showError=False,
                       callback=callback)

    yield_until(lambda : result[0] is not None)

    assert not result[0]
    assert not panel.SessionActive()

    result[0] = None

    panel.StartSession('central.xnat.org',
                       showError=False,
                       callback=callback)

    yield_until(lambda : result[0] is not None)

    assert result[0]
    assert panel.SessionActive()
    panel.EndSession()
    assert not panel.SessionActive()
