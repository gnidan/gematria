
import wx 

class ProgressStatusBar: 
    '''wx.Gauge placement into a single or multi-fielded wx.Statusbar. 
    Will completely fill the statusbar field. Note that the field size 
    should be fixed or the frame size should be fixed so that the 
    field dimension for the gauge do not change. Fixing the frame size 
    can be done by: 

        def OnSize (self, event): 
            self.SetSize (self.size) 
            event.Skip () 
        #end def 

    Ray Pasco 2005-05-21        ver. 1.00 
    ''' 

    def __init__ (self, parent, statusbar, sbarfields=1, sbarfield=0, maxcount=100): 

        rect = statusbar.GetFieldRect (sbarfield) 
        barposn = (rect [0], rect [1]) 

        # On MSW the X dimension returned from GetFieldRect for the last field is too small. 
        #   This hack fills the field but covers over the lower right frame resize handle, 
        #    but that's OK since the field size should be unchangable. 
        if (sbarfield+1 == sbarfields) and (wx.Platform == '__WXMSW__'): 
            barsize = (rect [2]+35, rect [3])   # completely fill the last field 
        else: 
            barsize = (rect [2],    rect [3]) 
        #end if 

        self.progbar = wx.Gauge (statusbar, -1, maxcount, barposn, barsize) 
    #end def 

    def SetValue (self, value): 
        self.progbar.SetValue (value) 
    #end def 

    def SetRange(self, range):
      self.progbar.SetRange(range)

    def Hide(self):
        self.progbar.Hide()

    def Show(self):
        self.progbar.Show()

