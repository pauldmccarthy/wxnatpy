#!/usr/bin/env python
#
# xnatbrowser.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import os.path as op
import wx
import wx.lib.newevent as wxevent

import xnat

import fsleyes_widgets.placeholder_textctrl as plctext
import fsleyes_widgets.autotextctrl         as autotext
import fsleyes_widgets.widgetgrid           as wgrid


"""
-------------------------------------------------------
| Host:     | Username:     | Password:     | Connect |
-------------------------------------------------------
| Project drop down box                               |
| experiment filter                                   |
| subject filter                                      |
-------------------------------------------------------
|Project
| - Project level file
| - Project level file
| - Project level file
| - Subject 1
|   - Subject level file
|   - Experiment 1
      - Experiment level file
|     - Scan 1
|       - Scan file 1
|       - Scan file 2
|     - Scan 2
|       - Scan file 1
|       - Scan file 2
|   - Experiment 2
|     - Experiment level file
|  - Subject 2

| Load | Cancel                                       |
-------------------------------------------------------

"""



XNAT_HIERARCHY = {
    'projects'    : ['subjects',           'resources'],
    'subjects'    : ['experiments',        'resources'],
    'experiments' : ['assessors', 'scans', 'resources'],
    'scans'       : ['resources'],
    'resources'   : ['files'],
}

XNAT_NAME_ATT = {
    'project'    : 'name',
    'subject'    : 'label',
    'experiment' : 'label',
    'scan'       : 'type',
    'resource'   : 'label',
    'file'       : 'id',
}

XNAT_INFO_ATTS = {
    'project'    : ['id', 'name'],
    'subject'    : ['id', 'label'],
    'experiment' : ['id', 'label'],
    'scan'       : ['id', 'type'],
    'resource'   : ['id', 'label', 'file_size'],
    'file'       : ['id', 'size'],
}

# Saved hosts
# Saved user account(s) (per saved host)

LABELS = {
    'host'         : 'Host',
    'username'     : 'Username',
    'password'     : 'Password',
    'connect'      : 'Connect',
    'disconnect'   : 'Disconnect',
    'project'      : 'Project',
    'dialogTitle'  : 'Browse XNAT repository',
    'connected'    : u'\u2022',
    'disconnected' : u'\u2022',
}


class XNATBrowserPanel(wx.Panel):


    def __init__(self,
                 parent,
                 knownHosts=None,
                 knownAccounts=None):
        """
        """

        if knownHosts    is None: knownHosts    = []
        if knownAccounts is None: knownAccounts = {}

        wx.Panel.__init__(self, parent)

        self.__host     = autotext.AutoTextCtrl(self)
        self.__username = plctext.PlaceholderTextCtrl(self, placeholder='guest')
        self.__password = plctext.PlaceholderTextCtrl(self, placeholder='guest')
        self.__connect  = wx.Button(self)
        self.__status   = wx.StaticText(self)
        self.__project  = wx.Choice(self)
        self.__splitter = wx.SplitterWindow(self,
                                            style=(wx.SP_LIVE_UPDATE |
                                                   wx.SP_BORDER))
        self.__info     = wgrid.WidgetGrid(self.__splitter)
        self.__browser  = wx.TreeCtrl(self.__splitter,
                                      style=(wx.TR_MULTIPLE    |
                                             wx.TR_NO_LINES    |
                                             wx.TR_HAS_BUTTONS |
                                             wx.TR_TWIST_BUTTONS))

        self.__splitter.SetMinimumPaneSize(50)
        self.__splitter.SplitHorizontally(self.__info, self.__browser)
        self.__splitter.SetSashPosition(50)
        self.__splitter.SetSashGravity(0.2)

        imagedir = op.join(op.dirname(__file__), '..', 'assets')

        images   = [op.join(imagedir, 'file.png'),
                    op.join(imagedir, 'folder_unloaded.png'),
                    op.join(imagedir, 'folder_loaded.png')]
        images   = [wx.Bitmap(i) for i in images]

        self.__fileImageId           = 0
        self.__unloadedFolderImageId = 1
        self.__loadedFolderImageId   = 2

        imageList = wx.ImageList(16, 16)
        for i in images:
            imageList.Add(images[0])
            imageList.Add(images[1])
            imageList.Add(images[2])

        self.__browser.AssignImageList(imageList)

        self.__hostLabel     = wx.StaticText(self)
        self.__usernameLabel = wx.StaticText(self)
        self.__passwordLabel = wx.StaticText(self)
        self.__projectLabel  = wx.StaticText(self)

        self.__status.SetFont(self.__status.GetFont().Larger().Larger())
        self.__host         .AutoComplete(knownHosts)
        self.__hostLabel    .SetLabel(LABELS['host'])
        self.__usernameLabel.SetLabel(LABELS['username'])
        self.__passwordLabel.SetLabel(LABELS['password'])
        self.__connect      .SetLabel(LABELS['connect'])
        self.__projectLabel .SetLabel(LABELS['project'])

        self.__host    .SetValue('xw2017-01.xnat.org')
        self.__username.SetValue('admin')
        self.__password.SetValue('R0tt3rd@m')
        # self.__host    .SetValue('10.1.1.17')
        # self.__username.SetValue('admin')
        # self.__password.SetValue('admin')

        self.__loginSizer   = wx.BoxSizer(wx.HORIZONTAL)
        self.__projectSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.__mainSizer    = wx.BoxSizer(wx.VERTICAL)

        self.__loginSizer.Add((5, 1))
        self.__loginSizer.Add(self.__hostLabel)
        self.__loginSizer.Add((5, 1))
        self.__loginSizer.Add(self.__host, proportion=1)
        self.__loginSizer.Add((5, 1))
        self.__loginSizer.Add(self.__usernameLabel)
        self.__loginSizer.Add((5, 1))
        self.__loginSizer.Add(self.__username, proportion=1)
        self.__loginSizer.Add((5, 1))
        self.__loginSizer.Add(self.__passwordLabel)
        self.__loginSizer.Add((5, 1))
        self.__loginSizer.Add(self.__password, proportion=1)
        self.__loginSizer.Add((5, 1))
        self.__loginSizer.Add(self.__connect)
        self.__loginSizer.Add((5, 1))
        self.__loginSizer.Add(self.__status)
        self.__loginSizer.Add((5, 1))

        self.__projectSizer.Add((5, 1))
        self.__projectSizer.Add(self.__projectLabel)
        self.__projectSizer.Add((5, 1))
        self.__projectSizer.Add(self.__project, proportion=1)
        self.__projectSizer.Add((5, 1))

        self.__mainSizer.Add((1, 10))
        self.__mainSizer.Add(self.__loginSizer, flag=wx.EXPAND)
        self.__mainSizer.Add((1, 10))
        self.__mainSizer.Add(self.__projectSizer, flag=wx.EXPAND)
        self.__mainSizer.Add((1, 10))
        self.__mainSizer.Add(self.__splitter, flag=wx.EXPAND, proportion=1)
        self.__mainSizer.Add((1, 10))

        self.SetSizer(self.__mainSizer)

        self.__connect.Bind(wx.EVT_BUTTON,              self.__onConnect)
        self.__project.Bind(wx.EVT_CHOICE,              self.__onProject)
        self.__browser.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.__onTreeActivate)
        self.__browser.Bind(wx.EVT_TREE_SEL_CHANGED,    self.__onTreeSelect)

        self.__session = None
        self.disconnect()


    def connect(self, host, username=None, password=None):
        """
        """

        if self.isConnected():
            self.disconnect()

        # TOOD show a message while connecting
        # TODO show error and return
        self.__session = xnat.connect(host,
                                      user=username,
                                      password=password)

        self.__connect.SetLabel(LABELS['disconnect'])
        self.__status.SetLabel(LABELS['connected'])
        self.__status.SetForegroundColour('#00ff00')


    def disconnect(self):

        if self.__session is not None:
            self.__session.disconnect()
            self.__session = None

        self.__connect.SetLabel(LABELS['connect'])
        self.__status.SetLabel(LABELS['disconnected'])
        self.__status.SetForegroundColour('#ff0000')
        self.__project.Clear()


    def isConnected(self):
        return self.__session is not None


    def __onConnect(self, ev):

        if self.isConnected():
            self.disconnect()
            return

        host     = self.__host    .GetValue()
        username = self.__username.GetValue()
        password = self.__password.GetValue()

        if not (host.startswith('http://') or
                host.startswith('https://')):
            host = 'https://' + host

        if username == '': username = None
        if password == '': password = None

        self.connect(host, username, password)

        # TOOD show a message while loading projects
        # TODO bail if no projects
        projects = self.__session.projects
        projects = [p.id for p in projects.listing]
        self.__project.SetItems(projects)

        self.__onProject()


    def __onProject(self, ev=None):

        project = self.__project.GetString(self.__project.GetSelection())

        self.__browser.DeleteAllItems()
        root = self.__browser.AddRoot(
            'project {}'.format(project),
            data=[self.__session.projects[project], 'projects'],
            image=self.__unloadedFolderImageId)
        self.__onTreeSelect(item=root)


    def __onTreeActivate(self, ev=None, item=None):

        if ev is not None:
            item = ev.GetItem()
            ev.Skip()

        obj, level = self.__browser.GetItemData(item)

        if level == 'files':

            print('XNATFileSelectEvent: {}'.format(obj.uri))

            ev = XNATFileSelectEvent(path=obj.uri)
            ev.SetEventObject(self)
            wx.PostEvent(self, ev)
            return

        print('Folder {}'.format(self.__browser.GetItemText(item)))

        if self.__browser.GetChildrenCount(item) > 0:
            return

        # TODO For objects with a larger number of children:
        #
        #       - show a dialog, allow the user to cancel the
        #         request
        #         OR
        #       - Only load up to e.g. 100 items, and have a
        #         button  allowing the user to load more
        #         OR
        #       - Prompt the user to select a range of items
        #         to load

        self.__browser.SetItemImage(item, self.__loadedFolderImageId)

        for catt in XNAT_HIERARCHY[level]:
            children = getattr(obj, catt, None)
            if children is None:
                continue

            for child in children.listing:

                label = XNAT_NAME_ATT[catt[:-1]]
                label = getattr(child, label)

                if catt == 'files': image = self.__fileImageId
                else:               image = self.__unloadedFolderImageId

                self.__browser.AppendItem(
                    item,
                    '{} {}'.format(catt[:-1], label),
                    image=image,
                    data=[child, catt])


    def __onTreeSelect(self, ev=None, item=None):

        if ev is not None:
            ev.Skip()
            item = ev.GetItem()

        obj, level = self.__browser.GetItemData(item)
        otype      = level[:-1]

        rows = [
            ('Type', otype),
        ]

        for att in XNAT_INFO_ATTS[otype]:
            print('Lookup {}.{} [{}]'.format(otype, att, obj))
            try:
                rows.append((att, str(getattr(obj, att))))
            except Exception:
                continue

        if level in XNAT_HIERARCHY:
            for catt in XNAT_HIERARCHY[level]:
                nchildren = len(getattr(obj, catt))
                rows.append((catt, str(nchildren)))

        self.__info.ClearGrid()
        self.__info.SetGridSize(len(rows), 2, growCols=(1, ))

        for i, (header, value) in enumerate(rows):
            self.__info.SetText(i, 0, header)
            self.__info.SetText(i, 1, value)

        self.__info.Refresh()


_XNATFileSelectEvent, _EVT_XNAT_FILE_SELECT_EVENT = wxevent.NewEvent()


EVT_XNAT_FILE_SELECT_EVENT = _EVT_XNAT_FILE_SELECT_EVENT
"""Identifier for the :data:`XNATFileSelectEvent`. """


XNATFileSelectEvent = _XNATFileSelectEvent
"""Event emitted when a file item in the XNAT tree viewer is selected,
either by it being double-clicked, or with the enter key pressed while
it is highlighted. Contains an attribute ``path``, which may be passed
to the :meth:`XNATBrowserPanel.download` method to download the file.
"""


class XNATBrowserDialog(wx.Dialog):

    def __init__(self, parent, *args, **kwargs):

        wx.Dialog.__init__(self,
                           parent,
                           title=LABELS['dialogTitle'],
                           style=wx.RESIZE_BORDER)

        self.__panel = XNATBrowserPanel(self, *args, **kwargs)

        self.__sizer = wx.BoxSizer(wx.VERTICAL)
        self.__sizer.Add(self.__panel, flag=wx.EXPAND, proportion=1)
        self.SetSizer(self.__sizer)

        self.__sizer.Layout()
        self.__sizer.Fit(self)


if __name__ == '__main__':
    app   = wx.App()
    # frame = wx.Frame(None)
    dlg = XNATBrowserDialog(None)
    dlg.SetSize((-1, 500))
    dlg.Show()
    app.MainLoop()
