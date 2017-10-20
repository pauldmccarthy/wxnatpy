#!/usr/bin/env python
#
# __init__.py - unit tests for wxnatpy
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


import wx


def run_with_wx(func, *args, **kwargs):

    propagateRaise = kwargs.pop('propagateRaise', True)
    startingDelay  = kwargs.pop('startingDelay',  500)
    finishingDelay = kwargs.pop('finishingDelay', 500)
    callAfterApp   = kwargs.pop('callAfterApp',   None)

    result = [None]
    raised = [None]

    app    = wx.App()
    frame  = wx.Frame(None)

    if callAfterApp is not None:
        callAfterApp()

    def wrap():

        try:
            if func is not None:
                result[0] = func(*args, **kwargs)

        except Exception as e:
            print(e)
            raised[0] = e

        finally:
            def finish():
                frame.Destroy()
                app.ExitMainLoop()
            wx.CallLater(finishingDelay, finish)

    frame.Show()

    wx.CallLater(startingDelay, wrap)

    app.MainLoop()

    if raised[0] and propagateRaise:
        raise raised[0]

    return result[0]
