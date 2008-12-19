#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import wx
import gnuradio.gr.gr_threading as _threading

wxDATA_EVENT = wx.NewEventType()

def EVT_DATA_EVENT(win, func):
	win.Connect(-1, -1, wxDATA_EVENT, func)

class DataEvent(wx.PyEvent):
	def __init__(self, data):
		wx.PyEvent.__init__(self)
		self.SetEventType (wxDATA_EVENT)
		self.data = data

	def Clone (self):
		self.__class__ (self.GetId())

class queue_watcher_thread(_threading.Thread):
	def __init__(self, rcvd_pktq, event_receiver):
		_threading.Thread.__init__(self)
		self.setDaemon(1)
		self.rcvd_pktq = rcvd_pktq
		self.event_receiver = event_receiver
		self.keep_running = True
		self.start()

	def stop(self):
		self.keep_running = False

	def run(self):
		while self.keep_running:
			msg = self.rcvd_pktq.delete_head()
			de = DataEvent (msg)
			wx.PostEvent (self.event_receiver, de)
			del de

class rdsPanel(wx.Panel):
	def __init__(self, msgq, *args, **kwds):
		kwds["style"] = wx.TAB_TRAVERSAL
		wx.Panel.__init__(self, *args, **kwds)
		self.label_1 = wx.StaticText(self, -1, "Frequency")
		self.label_2 = wx.StaticText(self, -1, "Station Name")
		self.label_3 = wx.StaticText(self, -1, "Program Type")
		self.label_4 = wx.StaticText(self, -1, "PI")
		self.label_5 = wx.StaticText(self, -1, "Radio Text")
		self.label_6 = wx.StaticText(self, -1, "Clock Time")
		self.label_7 = wx.StaticText(self, -1, "Alternative Frequencies")
		self.frequency = wx.StaticText(self, -1, "xxx.xx")
		self.station_name = wx.StaticText(self, -1, "xxxxxxxx")
		self.program_type = wx.StaticText(self, -1, "xxxxxxxx")
		self.program_information = wx.StaticText(self, -1, "xxxx")
		self.tp_flag = wx.StaticText(self, -1, "TP")
		self.ta_flag = wx.StaticText(self, -1, "TA")
		self.musicspeech_flag = wx.StaticText(self, -1, "MUS/SPE")
		self.monostereo_flag = wx.StaticText(self, -1, "MN/ST")
		self.artificialhead_flag = wx.StaticText(self, -1, "AH")
		self.compressed_flag = wx.StaticText(self, -1, "CMP")
		self.staticpty_flag = wx.StaticText(self, -1, "stPTY")
		self.radiotext = wx.StaticText(self, -1, "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
		self.clocktime = wx.StaticText(self, -1, "xxxxxxxxxx")
		self.alt_freq = wx.StaticText(self, -1, "xxxxxxxxxx")

		self.__set_properties()
		self.__do_layout()
		EVT_DATA_EVENT (self, self.display_data)
		watcher=queue_watcher_thread(msgq,self)

	def __set_properties(self):
		self.frequency.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
		self.station_name.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
		self.program_type.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
		self.program_information.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
		self.tp_flag.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
		self.ta_flag.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
		self.musicspeech_flag.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
		self.monostereo_flag.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
		self.artificialhead_flag.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
		self.compressed_flag.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
		self.staticpty_flag.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))

	def __do_layout(self):
		sizer_1 = wx.BoxSizer(wx.VERTICAL)
		grid_sizer_4 = wx.GridSizer(1, 4, 0, 0)
		grid_sizer_3 = wx.GridSizer(1, 2, 0, 0)
		grid_sizer_2 = wx.GridSizer(1, 7, 0, 0)
		grid_sizer_1 = wx.GridSizer(2, 4, 0, 0)

		grid_sizer_1.Add(self.label_1, 0, 
			wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
		grid_sizer_1.Add(self.label_2, 0, 
			wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
		grid_sizer_1.Add(self.label_3, 0, 
			wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
		grid_sizer_1.Add(self.label_4, 0, 
			wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
		grid_sizer_1.Add(self.frequency, 0, 
			wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
		grid_sizer_1.Add(self.station_name, 0, 
			wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
		grid_sizer_1.Add(self.program_type, 0, 
			wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
		grid_sizer_1.Add(self.program_information, 0, 
			wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
		sizer_1.Add(grid_sizer_1, 1, wx.EXPAND, 0)

		grid_sizer_2.Add(self.tp_flag, 0, 
			wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
		grid_sizer_2.Add(self.ta_flag, 0, 
			wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
		grid_sizer_2.Add(self.musicspeech_flag, 0, 
			wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
		grid_sizer_2.Add(self.monostereo_flag, 0, 
			wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
		grid_sizer_2.Add(self.artificialhead_flag, 0, 
			wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
		grid_sizer_2.Add(self.compressed_flag, 0, 
			wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
		grid_sizer_2.Add(self.staticpty_flag, 0, 
			wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
		sizer_1.Add(grid_sizer_2, 1, wx.EXPAND, 0)

		grid_sizer_3.Add(self.label_5, 0, 
			wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
		grid_sizer_3.Add(self.radiotext, 0, 
			wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
		sizer_1.Add(grid_sizer_3, 1, wx.EXPAND, 0)

		grid_sizer_4.Add(self.label_6, 0, 
			wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
		grid_sizer_4.Add(self.clocktime, 0, 
			wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
		grid_sizer_4.Add(self.label_7, 0, 
			wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
		grid_sizer_4.Add(self.alt_freq, 0, 
			wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
		sizer_1.Add(grid_sizer_4, 1, wx.EXPAND, 0)

		self.SetAutoLayout(True)
		self.SetSizer(sizer_1)
		sizer_1.Fit(self)
		sizer_1.SetSizeHints(self)

	def display_data(self,event):
		message = event.data
		if (message.type()==0):		 #program information
			self.program_information.SetLabel(message.to_string())
		elif (message.type()==1):	#station name
			self.station_name.SetLabel(message.to_string())
		elif (message.type()==2):	#program type
			self.program_type.SetLabel(message.to_string())
		elif (message.type()==3):	#flags
			flags=message.to_string()
			if (flags[0]=='1'):
				self.tp_flag.SetForegroundColour(wx.RED)
			else:
				self.tp_flag.SetForegroundColour(wx.LIGHT_GREY)
			if (flags[1]=='1'):
				self.ta_flag.SetForegroundColour(wx.RED)
			else:
				self.ta_flag.SetForegroundColour(wx.LIGHT_GREY)
			if (flags[2]=='1'):
				self.musicspeech_flag.SetLabel("Music")
				self.musicspeech_flag.SetForegroundColour(wx.RED)
			else:
				self.musicspeech_flag.SetLabel("Speech")
				self.musicspeech_flag.SetForegroundColour(wx.RED)
			if (flags[3]=='1'):
				self.monostereo_flag.SetLabel("Mono")
				self.monostereo_flag.SetForegroundColour(wx.RED)
			else:
				self.monostereo_flag.SetLabel("Stereo")
				self.monostereo_flag.SetForegroundColour(wx.RED)
			if (flags[4]=='1'):
				self.artificialhead_flag.SetForegroundColour(wx.RED)
			else:
				self.artificialhead_flag.SetForegroundColour(wx.LIGHT_GREY)
			if (flags[5]=='1'):
				self.compressed_flag.SetForegroundColour(wx.RED)
			else:
				self.compressed_flag.SetForegroundColour(wx.LIGHT_GREY)
			if (flags[6]=='1'):
				self.staticpty_flag.SetForegroundColour(wx.RED)
			else:
				self.staticpty_flag.SetForegroundColour(wx.LIGHT_GREY)
		elif (message.type()==4):	#radiotext
			self.radiotext.SetLabel(message.to_string())
		elif (message.type()==5):	#clocktime
			self.clocktime.SetLabel(message.to_string())
#		elif (message.type()==6):	#alternative frequencies
#			self.alt_freq.SetLabel(message.to_string())
		elif (message.type()==9):	#lost sync - reset
			self.program_information.SetLabel("xxxx")
			self.station_name.SetLabel("xxxxxxxx")
			self.program_type.SetLabel("xxxxx")
			self.ta_flag.SetForegroundColour(wx.BLACK)
			self.tp_flag.SetForegroundColour(wx.BLACK)
			self.musicspeech_flag.SetLabel("MUS/SPE")
			self.musicspeech_flag.SetForegroundColour(wx.BLACK)
			self.monostereo_flag.SetLabel("MN/ST")
			self.monostereo_flag.SetForegroundColour(wx.BLACK)
			self.artificialhead_flag.SetForegroundColour(wx.BLACK)
			self.compressed_flag.SetForegroundColour(wx.BLACK)
			self.staticpty_flag.SetForegroundColour(wx.BLACK)
			self.radiotext.SetLabel("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
			self.clocktime.SetLabel("xxxxxxxxxxxx")
			self.alt_freq.SetLabel("xxxxxxxxxxxx")
# end of class rdsPanel
