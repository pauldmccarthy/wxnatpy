#!/usr/bin/env python
#
# test_start_end.py - Tests starting/ending sessions
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import wx

from . import run_with_wx

from wxnat import XNATBrowserPanel

def test_start_end():
    run_with_wx(_test_start_end)
def _test_start_end():

    parent = wx.GetTopLevelWindows()[0]
    panel  = XNATBrowserPanel(parent)

    assert not panel.StartSession('not.a.xnat.server', showError=False)
    assert not panel.SessionActive()

    assert panel.StartSession('central.xnat.org', showError=False)
    assert panel.SessionActive()
    panel.EndSession()
    assert not panel.SessionActive()
