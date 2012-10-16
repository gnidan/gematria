#!/usr/bin/python
# coding=utf8

import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin, ColumnSorterMixin
import sys
from threading import *
import codecs

import progsbar

from db import WordDatabase
from words import WordController

ID_SEARCH = wx.NewId()
ID_ADD = wx.NewId()
ID_WHOLE_WORD = wx.NewId()
ID_RESET_DB = wx.NewId()

EVT_WORD = wx.NewId()

DATABASE='words.db'

class WordEvent(wx.PyEvent):
  def __init__(self, data):
    wx.PyEvent.__init__(self)
    self.SetEventType(EVT_WORD)
    self.data = data

def file_len(fname):
  f = open(fname)
  lines = sum(1 for line in f)
  f.close()
  return lines

class Loader(Thread):
  def __init__(self, parent, fname):
    Thread.__init__(self)
    self.parent = parent
    self.want_abort = 0
    self.fname = fname
    self.start()

  def run(self):
    db = WordDatabase(DATABASE)
    words = WordController(db)
    db.empty()

    file = codecs.open(self.fname, encoding='utf-8')
    processed = 0
    for word in file:
      words.add_word(word, False)
      processed += 1
      wx.PostEvent(self.parent, WordEvent(processed))

    words.finish_adding()
    db.close()
    wx.PostEvent(self.parent, WordEvent(-1))

class WordList(wx.ListCtrl, ListCtrlAutoWidthMixin):
  def __init__(self, controller, parent, id):
    wx.ListCtrl.__init__(self, parent, id,
      style=wx.LC_REPORT | wx.LC_VIRTUAL | wx.LC_HRULES) 
    ListCtrlAutoWidthMixin.__init__(self)

    self.words = controller.get_words()
    self.controller = controller

    self.InsertColumn(0, 'Word', width=200)
    self.InsertColumn(1, 'Gematria Value', width=115)

    self.Refresh()

  def Refresh(self):
    self.SetItemCount(len(self.words))
    self.itemDataMap = dict([(i, self.words[i]) for i in 
      range(len(self.words))])

  def OnGetItemText(self, item, col): 
    return self.words[item][col]

class GematriaApp(wx.Frame):
  def __init__(self, parent, id, title):
    wx.Frame.__init__(self, parent, id, title, size=(350, 600))

    self.SetupDB()
    self.SetupUI()

  def SetupDB(self):
    self.db = WordDatabase(DATABASE)
    self.words = WordController(self.db)

  def SetupMenu(self):
    self.menu_bar  = wx.MenuBar()
    self.file_menu = wx.Menu()

    self.file_menu.Append(wx.ID_ABOUT,   "&About")
    self.file_menu.Append(wx.ID_EXIT, "&Quit")
    self.file_menu.Append(ID_RESET_DB, "&Reload Database with File...")

    self.menu_bar.Append(self.file_menu, "&File")

    self.SetMenuBar(self.menu_bar)
    self.Bind(wx.EVT_MENU, self.OnAbout, id=wx.ID_ABOUT)
    self.Bind(wx.EVT_MENU, self.OnQuit, id=wx.ID_EXIT)
    self.Bind(wx.EVT_MENU, self.OnReset, id=ID_RESET_DB)

  def SetupToolbar(self):
    toolbar = self.CreateToolBar(style=wx.TB_TEXT)
    self.search = wx.SearchCtrl(toolbar, ID_SEARCH)
    self.whole_word = wx.CheckBox(toolbar, ID_WHOLE_WORD)
    self.whole_word.SetValue(True)
    
    self.add = toolbar.AddLabelTool(ID_ADD, 'Add Word',
        wx.Bitmap('plus.png'))
    toolbar.AddStretchableSpace()
    toolbar.AddControl(self.search, "Search Word or Value")
    toolbar.AddControl(self.whole_word, "Search whole word")

    toolbar.Realize()

    self.toolbar = toolbar

    self.Bind(wx.EVT_TEXT, self.OnSearch, id=ID_SEARCH)
    self.Bind(wx.EVT_TOOL, self.AddWord, id=ID_ADD)
    self.Bind(wx.EVT_CHECKBOX, self.OnSearch, id=ID_WHOLE_WORD)

  def SetupUI(self):
    self.SetupMenu()
    self.SetupToolbar()

    self.statusbar = self.CreateStatusBar()
    self.statusbar.SetFieldsCount(2)
    self.progbar = progsbar.ProgressStatusBar(self, self.statusbar,
        2, 1, 100)
    self.progbar.Hide()
    self.Connect(-1, -1, EVT_WORD, self.OnWord)

    hbox = wx.BoxSizer(wx.HORIZONTAL)
    panel = wx.Panel(self, -1)

    self.lst = WordList(self.words, panel, -1)
    self.lst.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

    hbox.Add(self.lst, 1, wx.EXPAND | wx.ALL, 10)
    panel.SetSizer(hbox)

    self.Centre()
    self.Show(True)

    self.lst.Refresh()
    self.statusbar.SetStatusText("%s words in collection" % 
        "{:,}".format(self.words.num_words()), 1)

  def Refresh(self):
    text = self.search.Value
    try:
      value = int(text)
    except:
      value = None

    if value is not None:
      self.lst.words = self.words.query_value(value)
    elif len(text) > 0:
      whole_word = self.whole_word.IsChecked()
      self.lst.words = self.words.find_words(text, whole_word)
    else:
      self.lst.words = self.words.get_words()

    searchResults = len(self.lst.words)
    if value is None and searchResults == 0 and len(text) > 0:
      self.lst.words = [("(+) " + text, self.words.check_word(text))]

    num_words = self.words.num_words()
    self.statusbar.SetStatusText("%s words in collection" % 
        "{:,}".format(num_words), 1)

    self.lst.Refresh()

    if len(self.search.Value) > 0:
      self.statusbar.SetStatusText("%s search result%s" % 
        ("{:,}".format(searchResults), 's' if searchResults != 1 else ''),
        0)
    else:
      self.statusbar.SetStatusText("", 0)

  def OnSearch(self, event):
    self.Refresh()

  def AddWord(self, event):
    searchValue = self.search.Value
    if searchValue.isdigit():
      searchValue = ''

    text = wx.GetTextFromUser('Add word to collection', 'Insert Dialog',
      searchValue)
    if len(text) > 0:
      self.words.add_word(text)

    self.Refresh()

  def OnKeyDown(self, event):
    key = event.GetKeyCode()
    if key == wx.WXK_DELETE or key == wx.WXK_BACK:
      words = []
      idx = self.lst.GetFirstSelected()
      while idx != -1:
        words.append(self.lst.words[idx][0])
        idx = self.lst.GetNextSelected(idx)
      
      if len(words) > 1:
        msg = "Are you sure you want to remove these words?"
      elif len(words) == 1:
        msg = "Are you sure you want to remove this word?"
      else:
        return

      dlg = wx.MessageDialog(self, '\n'.join(words),
        msg,
        wx.OK|wx.CANCEL|wx.ICON_WARNING)
      result = dlg.ShowModal()
      dlg.Destroy()

      if result == wx.ID_OK:
        for word in words:
          self.words.del_word(word)
        self.Refresh()
  
  def OnAbout(self, event):
    dlg = wx.MessageDialog(self, 
        "(c) 2012 G. Nicholas D'Andrea <nick@gnidan.org>\n" +
        "Creative Commons License\n\n" +
        "Made for Sachio Takashima; Happy Birthday Sachio!",
        "Gematria Value Calculator", wx.OK|wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()
    self.statusbar.SetStatusText('', 0)

  def OnQuit(self, event):
    self.Destroy()

  def OnReset(self, event):
    dlg = wx.FileDialog(self, "Choose words file to reload database",
      style=wx.FD_OPEN)
    if dlg.ShowModal() == wx.ID_OK:
      fname = dlg.GetPath()
      length = file_len(fname)
      self.progbar.SetRange(length)
      self.statusbar.SetStatusText('', 1)
      self.progbar.Show()
      self.search.Disable()
      self.toolbar.EnableTool(ID_ADD, False)
      self.toolbar.EnableTool(ID_WHOLE_WORD, False)

      loader = Loader(self, fname)

    dlg.Destroy()

  def OnWord(self, event):
    if event.data == -1:
      self.progbar.Hide()
      self.search.Enable()
      self.toolbar.EnableTool(ID_ADD, True)
      self.toolbar.EnableTool(ID_WHOLE_WORD, True)
      self.Refresh()
    else:
      self.progbar.SetValue(event.data)

app = wx.App()
GematriaApp(None, -1, 'Gematria')
app.MainLoop()
