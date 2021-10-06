#!/usr/bin/env python


import wx
import sys
import logging

from wxnat.browser import XNATBrowserDialog


def main():

    if '-v' in sys.argv:
        logging.basicConfig()
        logging.getLogger('wxnat').setLevel(logging.DEBUG)

    app = wx.App()
    dlg = XNATBrowserDialog(None)
    dlg.SetSize((-1, 500))
    dlg.Show()

    if '-s' in sys.argv:
        def connect():
            dlg.browser.StartSession('central.xnat.org')
        wx.CallAfter(connect)

    app.MainLoop()



if __name__ == '__main__':
    main()
