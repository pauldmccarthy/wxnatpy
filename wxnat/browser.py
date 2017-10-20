#!/usr/bin/env python
#
# xnatbrowser.py -  The XNATBrowserPanel class.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides the :class:`XNATBrowserPanel`, a ``wx`` panel which
allows the user to connect to an XNAT server, and browse the projects and
files contained on it. The ``xnatpy`` library is used for communication with
the XNAT server.

Another class, the :class:`.XNATBrowserDialog` is also contained in this
module. This is a simple ``wx.Dialog`` which contains a ``XNATBrowserPanel``,
and *Download* and *Cancel* buttons.
"""


import os.path         as op
import                    re
import                    fnmatch

import                    wx
import wx.lib.newevent as wxevent

import xnat

import fsleyes_widgets.placeholder_textctrl as pt
import fsleyes_widgets.autotextctrl         as at
import fsleyes_widgets.utils.status         as status
import fsleyes_widgets.utils.progress       as progress
import fsleyes_widgets.widgetgrid           as wgrid


XNAT_HIERARCHY = {
    'project'     : ['subjects',           'resources'],
    'projects'    : ['subjects',           'resources'],
    'subject'     : ['experiments',        'resources'],
    'subjects'    : ['experiments',        'resources'],
    'experiment'  : ['assessors', 'scans', 'resources'],
    'experiments' : ['assessors', 'scans', 'resources'],
    'assessor'    : ['scans', 'resources'],
    'assessors'   : ['scans', 'resources'],
    'scan'        : ['resources'],
    'scans'       : ['resources'],
    'resource'    : ['files'],
    'resources'   : ['files'],
}
"""This dictionary defines the hierarchy used in XNAT, allowing the panel to
traverse the hierarchy without knowing the names of the attributes on the
``xnat.Session`` instance.
"""


XNAT_NAME_ATT = {
    'project'    : 'name',
    'subject'    : 'label',
    'experiment' : 'label',
    'scan'       : 'type',
    'resource'   : 'label',
    'file'       : 'id',
}
"""This dictionary defines the attribute to use as the name for objects at
each level of the XNAT hierarchy.
"""


XNAT_INFO_ATTS = {
    'project'    : ['id', 'name'],
    'subject'    : ['id', 'label'],
    'experiment' : ['id', 'label'],
    'scan'       : ['id', 'type'],
    'assessor'   : ['id'],
    'resource'   : ['id', 'label', 'file_size'],
    'file'       : ['id', 'size'],
}
"""This dictionary defines the attributes to show in the information panel for
highlihgted objects at each level of the XNAT hierarchy.
"""


LABELS = {
    'host'         : 'Host',
    'username'     : 'Username',
    'password'     : 'Password',
    'connect'      : 'Connect',
    'disconnect'   : 'Disconnect',
    'connecting'   : 'Connecting to {} ...',
    'project'      : 'Project',
    'refresh'      : 'Refresh',
    'connected'    : u'\u2022',
    'disconnected' : u'\u2022',

    'subjFilter' : 'Filter by subject',
    'expFilter'  : 'by experiment',

    'connect.error.title'   : 'Connection error',
    'connect.error.message' :
    'An error occurred while trying to connect to {}',


    'download.title'         : 'Downloading file',
    'download.startMessage'  : 'Downloading {} ...',
    'download.updateMessage' : 'Downloading {} ({:0.2f} of {:0.2f} MB)',

    'download.exists.title'   : 'File already exists',
    'download.exists.message' :
    'A file with the name {} already exists. What do you want to do?',

    'download.exists.overwrite' : 'Overwrite',
    'download.exists.newdest'   : 'Choose new name',
    'download.exists.skip'      : 'Skip',

    'download.exists.choose'    : 'Choose a new destination',

    'download.error.title'   : 'Download error',
    'download.error.message' :
    'An error occurred while trying to download {}',



    'projects'    : 'Projects',
    'project'     : 'Project',
    'subjects'    : 'Subjects',
    'subject'     : 'Subject',
    'experiments' : 'Experiments',
    'experiment'  : 'Experiment',
    'scans'       : 'Scans',
    'scan'        : 'Scan',
    'assessors'   : 'Assessors',
    'assessor'    : 'Assessor',
    'resource'    : 'Resource',
    'resources'   : 'Resources',
    'resource'    : 'Resource',
    'files'       : 'Files',
    'file'        : 'File',

    'project.id'         : 'ID',
    'project.name'       : 'Name',
    'subject.id'         : 'ID',
    'subject.label'      : 'Label',
    'experiment.id'      : 'ID',
    'experiment.label'   : 'Label',
    'scan.id'            : 'ID',
    'scan.type'          : 'Type',
    'resource.id'        : 'ID',
    'resource.label'     : 'Label',
    'resource.file_size' : 'Total size',
    'file.id'            : 'Name',
    'file.size'          : 'Size',
}
"""This dictionary contains labels used for various things in the user
interface.
"""


XNAT_INFO_FORMATTERS = {
    'resource.file_size' : lambda s: '{:0.2f} MB'.format(float(s) / 1048576),
    'file.size'          : lambda s: '{:0.2f} MB'.format(float(s) / 1048576)
}
"""This dictionary contains string formatters for some attributes that are
shown in the information panel.
"""


class XNATBrowserPanel(wx.Panel):
    """The ``XNATBrowserPanel`` allows the user to connect to and browse
    a XNAT repository. It contains:

     - controls allowing the user to enter a XNAT host and login
       credentials, and to connect to the host

     - A drop down box allowing the user to select a project on the
       XNAT host

     - A tree browser allowing the user to browse the contents of the
       currently selected project

     - A panel which displays information about the currently selected
       item in the tree browser.

    When the user double-clicks on a file object in the tree browser,
    a :class:`XNATFileSelectEvent`` is generated.

    The ``XNATBrowserPanel`` has a handful of useful methods:

    .. autosummary::
       :nosignatures:

       GetSelectedFiles
       DownloadFile
    """


    def __init__(self,
                 parent,
                 knownHosts=None,
                 knownAccounts=None,
                 filterType=None):
        """Create a ``XNATBrowserPanel``.

        :arg parent:        ``wx`` parent object.

        :arg knownHosts:    A sequence of hosts to be used as auto-complete
                            options in the host input field.

        :arg knownAccounts: A mapping of ``{ host : (username, password) }``,
                            which are used to automatically fill in the
                            login credentials when a particular host name
                            is entered.

        :arg filterType:    How the filter patterns should be applied -
                            either ``'regexp'`` for regular expressions, or
                            ``'glob'`` for shell-style wildcard patterns.
                            Defaults to ``'regexp'``.
        """

        if knownHosts    is None: knownHosts    = []
        if knownAccounts is None: knownAccounts = {}
        if filterType    is None: filterType    = 'regexp'

        if filterType not in ('regexp', 'glob'):
            raise ValueError('Unrecognised value for filterType: '
                             '{}. May be one of \'regexp\' or '
                             '\'glob\''.format(filterType))

        wx.Panel.__init__(self, parent)

        self.__knownAccounts = dict(knownAccounts)
        self.__filterType    = filterType

        self.__host       = at.AutoTextCtrl(self)
        self.__username   = pt.PlaceholderTextCtrl(self,
                                                   placeholder='username')
        self.__password   = pt.PlaceholderTextCtrl(self,
                                                   placeholder='password',
                                                   style=wx.TE_PASSWORD)
        self.__connect    = wx.Button(self)
        self.__status     = wx.StaticText(self)
        self.__project    = wx.Choice(self)
        self.__refresh    = wx.Button(self)

        self.__subjFilter = pt.PlaceholderTextCtrl(self,
                                                   placeholder=filterType,
                                                   style=wx.TE_PROCESS_ENTER)
        self.__expFilter  = pt.PlaceholderTextCtrl(self,
                                                   placeholder=filterType,
                                                   style=wx.TE_PROCESS_ENTER)
        self.__splitter   = wx.SplitterWindow(self,
                                              style=(wx.SP_LIVE_UPDATE |
                                                     wx.SP_BORDER))
        self.__info       = wgrid.WidgetGrid(self.__splitter)
        self.__browser    = wx.TreeCtrl(self.__splitter,
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

        self.__hostLabel       = wx.StaticText(self)
        self.__usernameLabel   = wx.StaticText(self)
        self.__passwordLabel   = wx.StaticText(self)
        self.__projectLabel    = wx.StaticText(self)
        self.__subjFilterLabel = wx.StaticText(self)
        self.__expFilterLabel  = wx.StaticText(self)

        self.__status.SetFont(self.__status.GetFont().Larger().Larger())
        self.__info.SetColours(border=self.__info._defaultEvenColour)
        self.__host           .AutoComplete(knownHosts)
        self.__hostLabel      .SetLabel(LABELS['host'])
        self.__usernameLabel  .SetLabel(LABELS['username'])
        self.__passwordLabel  .SetLabel(LABELS['password'])
        self.__connect        .SetLabel(LABELS['connect'])
        self.__projectLabel   .SetLabel(LABELS['project'])
        self.__subjFilterLabel.SetLabel(LABELS['subjFilter'])
        self.__expFilterLabel .SetLabel(LABELS['expFilter'])
        self.__refresh        .SetLabel(LABELS['refresh'])

        self.__loginSizer  = wx.BoxSizer(wx.HORIZONTAL)
        self.__filterSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.__mainSizer   = wx.BoxSizer(wx.VERTICAL)

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

        self.__filterSizer.Add((5, 1))
        self.__filterSizer.Add(self.__projectLabel)
        self.__filterSizer.Add((5, 1))
        self.__filterSizer.Add(self.__project, proportion=1)
        self.__filterSizer.Add((5, 1))
        self.__filterSizer.Add(self.__subjFilterLabel)
        self.__filterSizer.Add((5, 1))
        self.__filterSizer.Add(self.__subjFilter, proportion=1)
        self.__filterSizer.Add((5, 1))
        self.__filterSizer.Add(self.__expFilterLabel)
        self.__filterSizer.Add((5, 1))
        self.__filterSizer.Add(self.__expFilter, proportion=1)
        self.__filterSizer.Add((5, 1))
        self.__filterSizer.Add(self.__refresh)
        self.__filterSizer.Add((5, 1))

        self.__mainSizer.Add(self.__loginSizer, flag=wx.EXPAND)
        self.__mainSizer.Add((1, 10))
        self.__mainSizer.Add(self.__filterSizer, flag=wx.EXPAND)
        self.__mainSizer.Add((1, 10))
        self.__mainSizer.Add(self.__splitter, flag=wx.EXPAND, proportion=1)

        self.SetSizer(self.__mainSizer)

        self.__host   .Bind(at.EVT_ATC_TEXT_ENTER,       self.__onHost)
        self.__connect.Bind(wx.EVT_BUTTON,               self.__onConnect)
        self.__project.Bind(wx.EVT_CHOICE,               self.__onProject)
        self.__refresh.Bind(wx.EVT_BUTTON,               self.__onRefresh)
        self.__browser.Bind(wx.EVT_TREE_ITEM_ACTIVATED,  self.__onTreeActivate)
        self.__browser.Bind(wx.EVT_TREE_SEL_CHANGED,     self.__onTreeSelect)

        self.__subjFilter.Bind(wx.EVT_TEXT_ENTER, self.__onSubjectFilter)
        self.__expFilter .Bind(wx.EVT_TEXT_ENTER, self.__onExperimentFilter)

        self.__session = None
        self.__endSession()


    def GetSelectedFiles(self):
        """Returns a list of ``xnat`` objects representing all of the
        files that are currently selected in the tree browser.
        """
        items = self.__browser.GetSelections()
        files = []

        for i in items:

            obj, level = self.__browser.GetItemData(i)

            if level == 'file':
                files.append(obj)

        return files


    def DownloadFile(self, fobj, dest, showProgress=True):
        """Download the given ``xnat`` file object to the path specified by
        ``dest``.
        """

        fname = fobj.id
        fsize = fobj.size

        # if destination already exists, ask
        # thed user if they want to skip,
        # overwrite, or choose a new name
        if op.exists(dest):

            # We potentially show two dialogs -
            # the first one asking the user what
            # they want to do, and the second
            # one prompting for a new file. If
            # the user cancels the second dialog,
            # he/she is re-shown the first.
            while True:
                dlg = wx.MessageDialog(
                    self,
                    message=LABELS['download.exists.message'].format(fname),
                    caption=LABELS['download.exists.title'],
                    style=(wx.YES_NO |
                           wx.CANCEL |
                           wx.CENTRE |
                           wx.ICON_QUESTION))

                dlg.SetYesNoCancelLabels(
                    LABELS['download.exists.overwrite'],
                    LABELS['download.exists.newdest'],
                    LABELS['download.exists.skip'])

                choice = dlg.ShowModal()

                # overwrite
                if choice == wx.ID_YES:
                    break

                # skip
                elif choice == wx.ID_CANCEL:
                    return

                # choose a new destination
                elif choice == wx.ID_NO:
                    dlg = wx.FileDialog(
                        self,
                        message=LABELS['download.exists.choose'],
                        defaultDir=op.dirname(dest),
                        defaultFile=fname,
                        style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

                    # If user cancelled this dialog,
                    # show them the first dialog again.
                    if dlg.ShowModal() == wx.ID_OK:
                        dest  = dlg.GetPath()
                        fname = op.basename(dest)
                        break

        if showProgress:

            dlg = wx.ProgressDialog(
                LABELS['download.title'],
                LABELS['download.startMessage'].format(fname),
                maximum=int(fsize),
                parent=self)

            msg = LABELS['download.updateMessage']

            def update(nbytes, total, finished):

                nmb = nbytes / 1048576.
                tmb = total  / 1048576.

                dlg.Update(nbytes, msg.format(fname, nmb, tmb))
                dlg.Fit()

                if finished:
                    dlg.EndModal(wx.ID_OK)

            dlg.Show()

        else:
            update = None

        errTitle = LABELS['download.error.title']
        errMsg   = LABELS['download.error.message'].format(fname)

        with status.reportIfError(errTitle, errMsg, raiseError=False):
            with open(dest, 'wb') as f:
                fobj.download_stream(f, update_func=update)

        if showProgress:
            dlg.Close()


    def SessionActive(self):
        """Returns ``True`` if a connection to a server is open, ``False``
        otherwise.
        """
        return self.__session is not None


    def __startSession(self, host, username=None, password=None):
        """Opens a connection  to the given host, and updates the interface.

        :returns: ``True`` if the connection was successful, ``False``
                  otherwise.
        """

        if self.SessionActive():
            self.__endSession()

        # If protocol not specified,
        # try both https and http
        if host.startswith('http://') or host.startswith('https://'):
            hosts = [host]
        else:
            hosts = ['https://' + host, 'http://' + host]

        def success(session, host):
            self.__session = session
            self.__host.SetValue(host)
            self.__connect.SetLabel(LABELS['disconnect'])
            self.__status.SetLabel(LABELS['connected'])
            self.__status.SetForegroundColour('#00ff00')

        def failure(error):
            status.reportError(
                LABELS['connect.error.title'],
                LABELS['connect.error.message'].format(host),
                error)

        cancelled = [False]

        def connect():

            error = None

            for host in hosts:
                try:
                    session = xnat.connect(host,
                                           user=username,
                                           password=password)

                    if not cancelled[0]:
                        wx.CallAfter(success, session, host)
                    return

                except Exception as e:
                    error = e
                    if cancelled[0]:
                        return

            if not cancelled[0]:
                wx.CallAfter(failure, error)

        cancelled[0] = not progress.Bounce.runWithBounce(
            connect,
            'Connecting',
            LABELS['connecting'].format(host),
            style=wx.PD_APP_MODAL | wx.PD_CAN_ABORT)

        return not cancelled[0] and self.__session is not None


    def __endSession(self):
        """Disconnects any active session, and updates the interface."""

        if self.__session is not None:
            try:
                self.__session.disconnect()
            except Exception:
                # TODO log
                pass
            self.__session = None

        self.__connect.SetLabel(LABELS['connect'])
        self.__status.SetLabel(LABELS['disconnected'])
        self.__status.SetForegroundColour('#ff0000')
        self.__project.Clear()
        self.__browser.DeleteAllItems()
        self.__info.ClearGrid()
        self.__info.Refresh()


    def __getTreeContents(self):
        """Builds a representation of the current state of the XNAT hierarchy
        as displayed in the tree browser.

        :returns: The state of the tree, where each node is represented by a
                  tuple of the form ``(level, id, [children], expanded)``,
                  where:

                   - ``level`` is the item level in the XNAT hierarchy, e.g.
                     ``'project'``, ``'subject'``, etc.

                   - ``id`` is the XNAT id of the item

                   - ``[children]`` is a list of child items, or an empty list
                     if the item has no children

                   - ``expanded`` is ``True`` if the item is expanded in the
                     tree browser, ``False`` otherwise.

                  A reference to the root node is returned.
        """

        browser = self.__browser

        # Recursively build a copy of the tree
        # starting from the given treeItem.
        # Returns a representation of the item
        # as a tuple containing:
        #    ('level', 'id', [children], expanded)
        def buildTree(treeItem):

            obj, level = browser.GetItemData(treeItem)
            children   = []

            node = (obj.id, level, children, browser.IsExpanded(treeItem))

            if browser.GetChildrenCount(treeItem) == 0:
                return node

            (childItem, cookie) = browser.GetFirstChild(treeItem)
            while childItem.IsOk():
                children.append(buildTree(childItem))
                childItem, cookie = browser.GetNextChild(treeItem, cookie)

            return node

        return buildTree(browser.GetRootItem())


    def __expandTreeItem(self, obj, level, treeItem):
        """Expands the contents of the given ``treeItem`` in the tree browser.
        For each child level of the item's level in the XNAT hierarchy, any
        child objects are retrieved from the XNAT repository and added as items
        in the tree browser.

        :arg obj:      XNAT object

        :arg level:    Level of ``obj`` in the XNAT hierarchy

        :arg treeItem: ``wx.TreeItemId`` corresponding to ``obj``

        :returns:      A mapping of the form: ``{ xnat_id : (xnat_obj,
                       wx.TreeItemId) }``, containing the newly created
                       ``wx.TreeItemId`` objects orresponding to the
                       children of ``obj``.
        """

        childItems = {}

        if level != 'file':
            self.__browser.SetItemImage(treeItem, self.__loadedFolderImageId)

        for catt in XNAT_HIERARCHY[level]:

            children = getattr(obj, catt, None)
            catt     = catt[:-1]

            if children is None:
                continue

            for child in children.listing:

                name  = getattr(child, XNAT_NAME_ATT[catt])
                label = LABELS[catt]

                if self.__filterItem(catt, name):
                    continue

                if catt == 'file': image = self.__fileImageId
                else:              image = self.__unloadedFolderImageId

                childItem = self.__browser.AppendItem(
                    treeItem,
                    '{} {}'.format(label, name),
                    image=image,
                    data=[child, catt])

                childItems[child.id] = (child, childItem)

        return childItems


    def __refreshTree(self):
        """Called by various things. Re-generates the current state of the
        tree browser.
        """

        # Make a copy of the tree state - the tree is stored
        # as a list of ('level', 'id', [children]) nodes
        browser  = self.__browser
        rootNode = self.__getTreeContents()
        rootItem = browser.GetRootItem()
        selItem  = browser.GetFocusedItem()
        rootObj  = browser.GetItemData(rootItem)[0]

        if selItem.IsOk(): selObj = browser.GetItemData(selItem)[0]
        else:              selObj = None

        # Now clear the tree, and regenerate
        # it according to its previous state
        browser.DeleteChildren(rootItem)

        # Recursively add the children of
        # the given tree item to the tree
        def refresh(treeItem, treeNode, obj):

            objid, level, childNodes, expanded = treeNode

            if obj is selObj:
                browser.SetFocusedItem(treeItem)

            if len(childNodes) == 0:
                return

            childItems = self.__expandTreeItem(obj, level, treeItem)

            # Loop through the nodes of the previous tree
            # state, and expand any that have been newly
            # added during this refresh. Some nodes
            # which were in the tree may not be anymore,
            # as they may have been filtered out.
            for cnode in childNodes:

                cid         = cnode[0]
                cobj, citem = childItems.get(cid, (None, None))

                if citem is not None:
                    refresh(citem, cnode, cobj)

            if expanded: browser.Expand(  treeItem)
            else:        browser.Collapse(treeItem)

        refresh(rootItem, rootNode, rootObj)


    def __filterItem(self, level, name):
        """Tests the given ``name`` to see if it should be filtered from the
        tree browser.

        :arg level: XNAT hierarchy level, e.g. ``'subject'``, ``'experiment'``,
                    etc.

        :arg name:  Name of item to test.

        :returns:   ``True`` if the given item should be filtered, ``False``
                    otherwise.
        """

        pattern = ''

        if   level == 'subject':    pattern = self.__subjFilter.GetValue()
        elif level == 'experiment': pattern = self.__expFilter .GetValue()

        if pattern.strip() == '':
            return False

        if self.__filterType == 'regexp':
            return re.search(pattern, name, flags=re.IGNORECASE) is None
        elif self.__filterType == 'glob':
            return not fnmatch.fnmatch(name, pattern)
        else:
            return False


    def __onHost(self, ev):
        """Called when the user enters a host name. If the host is
        in the ``knownAccounts`` dictionary that was passed to
        :meth:`__init__`, the username/password fields are populated.
        """

        ev.Skip()

        host               = self.__host.GetValue()
        username, password = self.__knownAccounts.get(host, (None, None))

        if username is not None: self.__username.SetValue(username)
        if password is not None: self.__password.SetValue(password)


    def __onConnect(self, ev):
        """Called when the *Connect* button is pushed. Attempts to start
        a session with the XNAT host.
        """

        if self.SessionActive():
            self.__endSession()
            return

        host     = self.__host    .GetValue()
        username = self.__username.GetValue()
        password = self.__password.GetValue()

        if username == '': username = None
        if password == '': password = None

        if not self.__startSession(host, username, password):
            return

        projects = self.__session.projects
        projects = [p.id for p in projects.listing]

        self.__project.SetItems(projects)
        self.__onProject()


    def __onProject(self, ev=None):
        """Called when an item in the the *Project* drop down box is selected.
        Clears the browser tree, and creates a new root node for the newly
        selected project.
        """

        project = self.__project.GetString(self.__project.GetSelection())
        label   = LABELS['project']

        self.__browser.DeleteAllItems()

        # For each element in the tree, the xnat
        # object, and the name of its level in
        # the XNAT hierarchy (e.g 'project',
        # 'experiment') is stored by the tree
        # browser.
        root  = self.__browser.AddRoot(
            '{} {}'.format(label, project),
            data=[self.__session.projects[project], 'project'],
            image=self.__unloadedFolderImageId)

        self.__onTreeSelect(item=root)


    def __onRefresh(self, ev):
        """Called when the *Refresh* button is pushed. Clears the cache of all
        items that have been downloaded from the XNAT server, and refreshes
        the tree browser.
        """
        if self.SessionActive():
            self.__session.clearcache()
            self.__refreshTree()


    def __onSubjectFilter(self, ev):
        """Called when the user pushes the enter key in the subject filter
        field. Refreshes the tree browser with the new filter value.
        """
        if self.SessionActive():
            self.__refreshTree()


    def __onExperimentFilter(self, ev):
        """Called when the user pushes the enter key in the experiment filter
        field. Refreshes the tree browser with the new filter value.
        """
        if self.SessionActive():
            self.__refreshTree()


    def __onTreeActivate(self, ev=None, item=None):
        """Called when an item in the tree is double-clicked (or enter is
        pushed when an item is highlighted). If the item is a file, a
        :class:`XNATFileSelectEvent` is generated. Otherwise, if any
        children for the item have not yet been added, they are retrieved
        and added to the tree.
        """

        if ev is not None:
            item = ev.GetItem()
            ev.Skip()

        # Retrieve the XNAT object and its level
        # in the hierarchy from the tree browser.
        obj, level = self.__browser.GetItemData(item)

        # When a file gets activated,
        # post a file select event
        if level == 'file':
            ev = XNATFileSelectEvent(path=obj.uri)
            ev.SetEventObject(self)
            wx.PostEvent(self, ev)
            return

        # This item has already been expanded
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

        self.__expandTreeItem(obj, level, item)


    def __onTreeSelect(self, ev=None, item=None):
        """Called when an item is highlighted in the tree browser. Displays
        some metadata about the item in the information panel.
        """

        if ev is not None:
            ev.Skip()
            item = ev.GetItem()

        obj, level = self.__browser.GetItemData(item)

        rows = [
            ('Type', LABELS[level]),
        ]

        for att in XNAT_INFO_ATTS[level]:
            key = '{}.{}'.format(level, att)
            val = getattr(obj, att)
            fmt = XNAT_INFO_FORMATTERS.get(key, str)
            rows.append((LABELS[key], fmt(val)))

        if level in XNAT_HIERARCHY:
            for catt in XNAT_HIERARCHY[level]:

                nchildren = str(len(getattr(obj, catt)))
                catt      = LABELS[catt]

                rows.append((catt, nchildren))

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
    """The ``XNATBrowserDialog`` is a ``wx.Dialog`` which contains a
    :class:`XNATBrowserPanel`, and *Download* and *Cancel* buttons.
    """

    def __init__(self, parent, *args, **kwargs):
        """Create a ``XNATBrowserDialog``.

        :arg parent: ``wx`` parent object

        All other arguments are passed through to the ``XNATBrowserPanel``
        instance.
        """

        wx.Dialog.__init__(self,
                           parent,
                           title='Browse XNAT repository',
                           style=wx.RESIZE_BORDER)

        self.__panel    = XNATBrowserPanel(self, *args, **kwargs)
        self.__download = wx.Button(self)
        self.__close    = wx.Button(self, id=wx.ID_CLOSE)

        self.__download.SetLabel('Download')
        self.__close   .SetLabel('Close')

        self.__btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.__sizer    = wx.BoxSizer(wx.VERTICAL)

        self.__btnSizer.Add((10, 1),         flag=wx.EXPAND, proportion=1)
        self.__btnSizer.Add(self.__close,    flag=wx.EXPAND)
        self.__btnSizer.Add((10, 1),         flag=wx.EXPAND)
        self.__btnSizer.Add(self.__download, flag=wx.EXPAND)
        self.__btnSizer.Add((10, 1),         flag=wx.EXPAND)

        self.__sizer.Add((1, 10),         flag=wx.EXPAND)
        self.__sizer.Add(self.__panel,    flag=wx.EXPAND, proportion=1)
        self.__sizer.Add((1, 10),         flag=wx.EXPAND)
        self.__sizer.Add(self.__btnSizer, flag=wx.EXPAND)
        self.__sizer.Add((1, 10),         flag=wx.EXPAND)

        self.SetSizer(self.__sizer)

        self.__sizer.Layout()
        self.__sizer.Fit(self)

        self.__download.Bind(wx.EVT_BUTTON, self.__onDownload)
        self.__close   .Bind(wx.EVT_BUTTON, self.__onClose)


    def __onDownload(self, ev):
        """Called when the *Close* button is pushed. Prompts the user to
        select a local directory to download the files to, then downloads
        all of the selected files.
        """

        dlg = wx.DirDialog(self, 'Select a download location')

        if dlg.ShowModal() != wx.ID_OK:
            return

        files   = self.__panel.GetSelectedFiles()
        destDir = dlg.GetPath()

        for fobj in files:
            name = op.basename(fobj.id)
            dest = op.join(destDir, name)
            self.__panel.DownloadFile(fobj, dest)


    def __onClose(self, ev):
        """Called when the *Close* button is pushed. Closes the dialog. """

        if self.IsModal(): self.EndModal(wx.ID_CLOSE)
        else:              self.Close()


if __name__ == '__main__':
    app = wx.App()
    dlg = XNATBrowserDialog(None)
    dlg.SetSize((-1, 500))
    dlg.Show()
    app.MainLoop()
