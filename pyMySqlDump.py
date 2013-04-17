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

        button = wx.Button(self, -1, label="Dump'em all !")
        sizer.Add(button, (columnNum, 1))
        self.Bind(wx.EVT_BUTTON, self.OnButtonClick, button)

        sizer.AddGrowableCol(0)
        self.SetSizerAndFit(sizer)
        self.SetSizeHints(-1, self.GetSize().y, -1, self.GetSize().y)
        self.Show(True)

    def OnButtonClick(self, event):
        print "dumping..."
        for dbname in self.checkboxes.iterkeys():
            if self.checkboxes[dbname].GetValue():
                dbutil.dumpDatabase(dbname)

        #os.system("mysqldump -u %s --password=%s %s > %s%s.sql" % (self.username, self.password, dbname, self.path, dbname))


if __name__ == "__main__":
    app = wx.App()
    frame = simpleapp_wx(None, -1, 'pyMySqlDump')
    app.MainLoop()
