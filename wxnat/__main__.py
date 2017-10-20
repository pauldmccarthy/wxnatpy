#!/usr/bin/env python


import wx

from wxnat.browser import XNATBrowserDialog


def main():

    app = wx.App()
    dlg = XNATBrowserDialog(None)
    dlg.SetSize((-1, 500))
    dlg.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
