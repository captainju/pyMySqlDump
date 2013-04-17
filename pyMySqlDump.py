#!/usr/bin/python2
# -*- coding: iso-8859-1 -*-

import dbutil

try:
    import wx
except ImportError:
    raise ImportError("The wxPython module is required to run this program")


class simpleapp_wx(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title)
        self.checkboxes = {}
        self.parent = parent
        self.initialize()

    def initialize(self):

        sizer = wx.GridBagSizer()

        columnNum = 0
        for dbinfo in dbutil.getDatabasesNamesAndSizes():
            checkBox = wx.CheckBox(self, -1, label=dbinfo[0]+" ~"+str(int(dbinfo[1]))+" MB")
            checkBox.SetValue(True)
            self.checkboxes[dbinfo[0]] = checkBox
            sizer.Add(checkBox, (columnNum, 0))
            columnNum = columnNum + 1

        dumpButton = wx.Button(self, -1, label="Dump'em all !")
        sizer.Add(dumpButton, (columnNum, 1))
        self.Bind(wx.EVT_BUTTON, self.OnDumpButtonClick, dumpButton)

        allButton = wx.Button(self, -1, label="all")
        sizer.Add(allButton, (columnNum, 0))
        self.Bind(wx.EVT_BUTTON, self.OnAllButtonClick, allButton)

        noneButton = wx.Button(self, -1, label="none")
        sizer.Add(noneButton, (columnNum+1, 0))
        self.Bind(wx.EVT_BUTTON, self.OnNoneButtonClick, noneButton)

        sizer.AddGrowableCol(0)
        self.SetSizerAndFit(sizer)
        self.SetSizeHints(-1, self.GetSize().y, -1, self.GetSize().y)
        self.Show(True)

    def OnDumpButtonClick(self, event):
        print "dumping..."
        for dbname in self.checkboxes.iterkeys():
            if self.checkboxes[dbname].GetValue():
                dbutil.dumpDatabase(dbname)

    def OnAllButtonClick(self, event):
        for dbname in self.checkboxes.iterkeys():
            self.checkboxes[dbname].SetValue(True)

    def OnNoneButtonClick(self, event):
        for dbname in self.checkboxes.iterkeys():
            self.checkboxes[dbname].SetValue(False)


if __name__ == "__main__":
    app = wx.App()
    frame = simpleapp_wx(None, -1, 'pyMySqlDump')
    app.MainLoop()
