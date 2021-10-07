
#
# test_known_hosts.py - Tests that known/hosts/accounts work
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import wx

from . import run_with_wx, yield_until

from wxnat import XNATBrowserPanel


# Test that known hosts and accounts
# passed to init are preserved, even
# if they are invalid
def test_known_hosts():
    run_with_wx(_test_known_hosts)
def _test_known_hosts():

    hosts = [
        'not.a.xnat.server'
    ]

    accounts = {
        'not.a.xnat.server' : ('bah', 'humbug'),
    }

    parent = wx.GetTopLevelWindows()[0]
    panel = XNATBrowserPanel(parent, knownHosts=hosts, knownAccounts=accounts)

    result = [None]
    def callback(val):
        result[0] = val

    # anonymous login to central should work,
    # and should result in central.xnat.org
    # added to known hosts/accounts
    panel.StartSession('central.xnat.org', showError=False)
    yield_until(panel.SessionActive)
    panel.EndSession()

    # bad (hopefully!) login to
    # central should not work
    panel.StartSession('central.xnat.org',
                       username='not_a_username',
                       password='not_a_password',
                       showError=False,
                       callback=callback)
    yield_until(lambda : result[0] is not None)
    assert not result[0]
    assert not panel.SessionActive()
    result[0] = None

    # login to non-existent server
    # central should not work
    panel.StartSession('not.a.xnat.server',
                       username='not_a_username',
                       password='not_a_password',
                       showError=False,
                       callback=callback)
    yield_until(lambda : result[0] is not None)
    assert not result[0]
    assert not panel.SessionActive()
    result[0] = None

    hosts = [
        'not.a.xnat.server',
        'central.xnat.org'
    ]

    accounts = {
        'not.a.xnat.server' : ('bah', 'humbug'),
        'central.xnat.org'  : (None, None),
    }

    assert panel.GetHosts()    == hosts
    assert panel.GetAccounts() == accounts
