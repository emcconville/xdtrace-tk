#!/usr/bin/env python

from Tkinter import *
import tkFileDialog, tkSimpleDialog
import re, os, cPickle, hashlib, sqlite3

from xdbtrc.xt import Import
from xdbtrc.rc import Preferences, Preferences_Dialog

class Application(Frame) :
	stage = db_path = None
	graphes = []
	width, height = 760, 360
	
	def loadFile(self,event=None):
		foptions = {
			'title':'Please select a xDebug-Trace (.xt) File',
			'filetypes' : [('text files', '.xt'),('log files', '.xt')],
			'defaultextension' : 'xt',
			'parent' : self
		}
		filename = tkFileDialog.askopenfilename(**foptions)
		if len(filename) > 0 :
			self.db_path = Import(self.CANVAS,self.rc).process(filename)
			self.resetCanvas()
			self.buildCanvas(0)
	
	def buildCanvas(self,index):
		try:
			if self.CANVAS is None:
				raise Exception('Canvas')
			if self.db_path is None:
				raise Exception('Database path')
			if self.rc is None:
				raise Exception('Run-Configuration')
		except Exception as e:
			print "[%s] is undefined" % e
			return
		self.resetCanvas()
		self.stage = self.graphes[index]()
		self.stage.build(self.CANVAS,self.db_path,self.rc)
		
	def resetCanvas(self,event=None):
		try:
			if self.stage is not None:
				self.stage.destroy()
		except Exception as e:
			print 'Unable to destroy [%s]' % e
		self.CANVAS.delete('actor')
		self.CANVAS.update_idletasks()
	
	def pref_dialog(self):
		d = Preferences_Dialog(self)
		
	def loadGraphes(self):
		for root, dirs, files in os.walk(os.path.join('.','graphes')):
			for fname in files:
				_name = re.match(r"^([A-Z](.*?))\.py$",fname)
				if _name is not None:
					module = __import__("graphes.%s" % _name.group(1))
					graph = module.__dict__[_name.group(1)]
					self.graphes.append(graph.Stage)
		
	def initMenu(self):
		self.MENU_BAR = Menu(self.master)
		self.F_MENU = Menu(self.MENU_BAR,tearoff=0)
		self.F_MENU.add_command(label='Open',accelerator="Cmd+O",command=self.loadFile)
		self.F_MENU.add_separator()
		self.F_MENU.add_command(label='Preferences',command=self.pref_dialog)
		self.F_MENU.add_separator()
		self.F_MENU.add_command(label='Close',accelerator="Cmd+W",command=self.resetCanvas)
		self.F_MENU.add_command(label='Quit', accelerator="Cmd+Q",command=self.close)
		self.MENU_BAR.add_cascade(label='Files',menu=self.F_MENU)
		self.V_MENU = Menu(self.MENU_BAR,tearoff=0)
		i = 0
		for graph in self.graphes:
			self.V_MENU.add_command(label=graph.MENU_TITLE,command=lambda i=i: self.buildCanvas(i))
			i+=1
		self.MENU_BAR.add_cascade(label="Views",menu=self.V_MENU)
		self.master.config(menu=self.MENU_BAR)
		
	def initWidgets(self):
		self.loadGraphes()
		self.initMenu()
		self.CANVAS = Canvas(self,width=self['width'],height=self['height'])
		self.CANVAS.pack(fill='both', expand=1)
		self._border = self.CANVAS.create_rectangle(20,20,self.width-20,self.height-20,fill='white',width=1,outline='#cccccc')
		self.bind('<Configure>',self._update_canvas)
		self.bind_all('<Command-o>',self.loadFile)
		self.bind_all('<Command-w>',self.resetCanvas)
		self.bind_all('<Command-q>',self.close)
		
	def close(self,event=None):
		self.rc.save()
		if self.db_path is not None and os.path.exists(self.db_path):
			os.remove(self.db_path)
		self.master.quit()
	
	def __init__(self,master=None):
		self.rc = Preferences()
		Frame.__init__(self,master,width=self.width,height=self.height)
		self.master.title('xdbug-trace-tk')
		self.pack(fill='both', expand=1)
		self.initWidgets()
	
	def _update_canvas(self,event):
		self.width = self.winfo_width()
		self.height = self.winfo_height()
		self.CANVAS.coords(self._border,20,20,self.width-20,self.height-20)
		try:
			if self.stage is not None:
				self.stage.resize(self.width,self.height)
		except Exception:
				pass
		self.CANVAS.update_idletasks()




if __name__ == '__main__':
	root = Tk()
	Application(root).mainloop()
	try:
	  root.destroy()
	except TclError :
		print "Nothing to destroy"
	exit(0)