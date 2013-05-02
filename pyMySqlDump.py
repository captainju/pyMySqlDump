#!/usr/bin/python2
# -*- coding: iso-8859-1 -*-

import dbutil
import os
from time import gmtime, strftime
from threading import Thread

try:
    import wx
    import wx.lib.newevent
except ImportError:
    raise ImportError("The wxPython module is required to run this program")


dumpEvent, EVT_DUMP_EVENT = wx.lib.newevent.NewEvent()
connectionInfos = dbutil.ConnectionInfos()


def dump_thread(i, basesNb, frame, wx, dbname, path):
    dbutil.dumpDatabase(dbname, path, connectionInfos)
    evt = dumpEvent(number=i, basesNb=basesNb)
    wx.PostEvent(frame, evt)


class GetConnectionInfos(wx.Dialog):

    def __init__(self, *args, **kw):
        super(GetConnectionInfos, self).__init__(*args, **kw)

        self.InitUI()
        self.SetSize((250, 200))
        ico = wx.Icon('pyMySqlDump.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(ico)

    def InitUI(self):

        pnl = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        sb = wx.StaticBox(pnl, label='MySQL Parameters')
        sbs = wx.StaticBoxSizer(sb, orient=wx.VERTICAL)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.txtCtrl1 = wx.TextCtrl(pnl)
        self.txtCtrl1.write(connectionInfos.host)
        hbox1.Add(self.txtCtrl1, flag=wx.LEFT, border=5)
        sbs.Add(hbox1)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.txtCtrl2 = wx.TextCtrl(pnl)
        self.txtCtrl2.write(str(connectionInfos.port))
        hbox2.Add(self.txtCtrl2, flag=wx.LEFT, border=5)
        sbs.Add(hbox2)
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.txtCtrl3 = wx.TextCtrl(pnl)
        self.txtCtrl3.write(connectionInfos.user)
        hbox3.Add(self.txtCtrl3, flag=wx.LEFT, border=5)
        sbs.Add(hbox3)
        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        self.txtCtrl4 = wx.TextCtrl(pnl, style=wx.TE_PROCESS_ENTER)
        self.txtCtrl4.write(connectionInfos.password)
        self.txtCtrl4.Bind(wx.EVT_TEXT_ENTER, self.OnTry, self.txtCtrl4)
        hbox4.Add(self.txtCtrl4, flag=wx.LEFT, border=5)
        sbs.Add(hbox4)

        pnl.SetSizer(sbs)
        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self, label='Try')
        closeButton = wx.Button(self, label='Exit')
        hbox5.Add(okButton)
        hbox5.Add(closeButton, flag=wx.LEFT, border=5)

        vbox.Add(pnl, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        vbox.Add(hbox5, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)

        self.SetSizer(vbox)

        okButton.Bind(wx.EVT_BUTTON, self.OnTry)
        closeButton.Bind(wx.EVT_BUTTON, self.OnExit)

        self.txtCtrl1.SetFocus()

    def OnTry(self, e):
        connectionInfos.host = self.txtCtrl1.GetValue()
        connectionInfos.port = int(self.txtCtrl2.GetValue())
        connectionInfos.user = self.txtCtrl3.GetValue()
        connectionInfos.password = self.txtCtrl4.GetValue()
        if dbutil.tryConnect(connectionInfos) is not None:
            self.Close()
        else:
            wx.MessageBox('Try again !', "Info", wx.OK | wx.ICON_EXCLAMATION)
            self.txtCtrl1.SetFocus()

    def OnExit(self, e):
        self.Destroy()
        exit()


class DumpingApp(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title)
        self.parent = parent
        self.initialize()

    def initialize(self):
        ico = wx.Icon('pyMySqlDump.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(ico)

        self.checkboxes = {}
        self.abort = False
        self.threads = {}

        #do we have a connection ?
        self.isConnected = False
        if not self.isConnected:
            self.isConnected = self.get_connection_info()

        if self.isConnected:
            self.populate_db_dump()
        else:
            exit()

    def get_connection_info(self):
        if dbutil.tryConnect(connectionInfos) is None:
            chgdep = GetConnectionInfos(None, title='MySQL connection')
            chgdep.ShowModal()
            chgdep.Destroy()
        return dbutil.tryConnect(connectionInfos)

    def populate_db_dump(self):
        sizer = wx.GridBagSizer()

        self.Bind(EVT_DUMP_EVENT, self.handler_dump_event)

        columnNum = 0
        for dbinfo in dbutil.getDatabaseNamesAndSizes(connectionInfos):
            checkBox = wx.CheckBox(self, -1, label=dbinfo[0]+" ~"+str(int(dbinfo[1]))+" MB")
            checkBox.SetValue(True)
            self.checkboxes[dbinfo[0]] = checkBox
            sizer.Add(checkBox, (columnNum, 0))
            columnNum = columnNum + 1

        self.dumpButton = wx.Button(self, -1, label="Dump'em !")
        sizer.Add(self.dumpButton, (columnNum, 1))
        self.Bind(wx.EVT_BUTTON, self.on_dumpbutton_click, self.dumpButton)

        allButton = wx.Button(self, -1, label="all")
        sizer.Add(allButton, (columnNum, 0))
        self.Bind(wx.EVT_BUTTON, self.on_allbutton_click, allButton)

        noneButton = wx.Button(self, -1, label="none")
        sizer.Add(noneButton, (columnNum+1, 0))
        self.Bind(wx.EVT_BUTTON, self.on_nonebutton_click, noneButton)

        sizer.AddGrowableCol(0)
        self.SetSizerAndFit(sizer)
        self.SetSizeHints(-1, self.GetSize().y, -1, self.GetSize().y)
        self.Show(True)

    def on_dumpbutton_click(self, event):

        if len(self.threads) != 0:
            #during dump, canceling...
            self.abort = True
            return

        counter = 0
        for dbname in self.checkboxes.iterkeys():
            if self.checkboxes[dbname].GetValue():
                counter += 1
        if counter == 0:
            #no databases selected
            return

        path = self.get_store_path()
        if path != '':
            path = path + "/" + strftime("%Y%m%d_%H%M%S", gmtime())
            os.makedirs(path)
            self.threads = {}
            howManyBases = counter

            counter = 0
            for dbname in self.checkboxes.iterkeys():
                if self.checkboxes[dbname].GetValue():
                    counter += 1
                    #creates a thread for dumping this DB
                    self.threads[counter] = Thread(target=dump_thread, args=(counter, howManyBases, self, wx, dbname, path))

            #begin dumping
            self.threads[1].start()
            self.dumpButton.SetLabel("1/%s (stop)" % (howManyBases))

    def on_allbutton_click(self, event):
        for dbname in self.checkboxes.iterkeys():
            self.checkboxes[dbname].SetValue(True)

    def on_nonebutton_click(self, event):
        for dbname in self.checkboxes.iterkeys():
            self.checkboxes[dbname].SetValue(False)

    def get_store_path(self):
        dirname = ''
        dlg = wx.DirDialog(self, "Where to put ?", "")
        if dlg.ShowModal() == wx.ID_OK:
            dirname = dlg.GetPath()
        dlg.Destroy()
        return dirname

    def handler_dump_event(self, event):
        #event handler, every time a DB has been dumped
        self.dumpButton.SetLabel("%s/%s (stop)" % (event.number+1, event.basesNb))
        next = event.number+1
        if next in self.threads.keys() and not self.abort:
            #more DB to dump
            self.threads[next].start()
        elif self.abort:
            #canceling
            self.dumpButton.SetLabel("Dump'em !")
            wx.MessageBox('Canceled', "Info", wx.OK | wx.ICON_EXCLAMATION)
            self.threads = {}
            self.abort = False
        else:
            #no more DB to dump
            self.dumpButton.SetLabel("Dump'em !")
            wx.MessageBox('Complete !', "Info", wx.OK | wx.ICON_INFORMATION)
            self.threads = {}


if __name__ == "__main__":
    app = wx.App()
    frame = DumpingApp(None, -1, 'pyMySqlDump')
    app.MainLoop()
