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
        self.parent = parent
        self.initialize()

    def initialize(self):

        sizer = wx.GridBagSizer()

        columnNum = 1
        for dbinfo in dbutil.getDatabasesNamesAndSizes():
            checkBox = wx.CheckBox(self, -1, label=dbinfo[0]+" "+str(int(dbinfo[1]))+" MB")
            checkBox.SetValue(True)
            sizer.Add(checkBox, (columnNum, 0))
            columnNum = columnNum + 1

        button = wx.Button(self, -1, label="Dump !")
        sizer.Add(button, (columnNum, 1))
        self.Bind(wx.EVT_BUTTON, self.OnButtonClick, button)

        sizer.AddGrowableCol(0)
        self.SetSizerAndFit(sizer)
        self.SetSizeHints(-1, self.GetSize().y, -1, self.GetSize().y)
        self.Show(True)

    def OnButtonClick(self, event):
        print "dumping..."

if __name__ == "__main__":
    app = wx.App()
    frame = simpleapp_wx(None, -1, 'my application')
    app.MainLoop()
