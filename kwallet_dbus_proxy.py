#!/usr/bin/python
# -*- coding: utf-8 -*-

import dbus
import os

from exceptions import Exception
# from dbus.mainloop.glib import DBusGMainLoop

#os.system("DISPLAY=:0.0; notify-send 'hello' 2>/tmp/notify-error")

class KWalletDBusProxyError(Exception):
    pass

class OperationFailedError(KWalletDBusProxyError):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

class KeywordNotFoundException(KWalletDBusProxyError):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

class KWalletDBusProxy(object):

    kwallet = None
    appName = None
    handle = 0

    def __init__(self, app_name):
        self.appName = app_name

        try:
            bus = dbus.SessionBus()
            kwalletd_proxy = bus.get_object('org.kde.kwalletd','/modules/kwalletd')
            self.kwallet = dbus.Interface( kwalletd_proxy, "org.kde.KWallet")
        except (Exception),e:
            raise OperationFailedError("could not connect to dbus") 

        # Open KWallet 
        try:
            self.handle = self.kwallet.open(self.kwallet.localWallet(), 0, self.appName) 
        except (Exception),e:
            print e
            raise OperationFailedError("could not open kwallet")

        # Check if we have already a KWallet folder
        if not self.kwallet.hasFolder(self.handle, self.appName, self.appName):
            self.kwallet.createFolder(self.handle, self.appName, self.appName)
            print "folder %s created" % (self.appName)

    
    def storeValue(self, keyword, value):
        try:
            self.kwallet.writePassword(self.handle, self.appName, keyword, value, self.appName)
        except (Exception),e:
            raise OperationFailedError("storing value failed") 
        


    def getValue(self, keyword):
        if not self.kwallet.hasEntry(self.handle, self.appName, keyword, self.appName):
            raise KeywordNotFoundException("key doesn't exist in KWallet");
        try:
            passwd = self.kwallet.readPassword(self.handle, self.appName, keyword, self.appName)
        except (Exception),e:
            raise OperationFailedError("reading value failed") 

        return passwd


if __name__ == "__main__":
    try:
        obj = KWalletDBusProxy("my_app")
    except (OperationFailedError), e:
        print e
        os.exit(1)

    try:
        obj.getValue("peter");
    except (KeywordNotFoundException),e:
        obj.storeValue("peter", "topgeheim");


    print obj.getValue("peter");
