#!/usr/bin/env python

import re, os
import Tkinter, tkFileDialog

from xdbtrc.xt import Import
from xdbtrc.rc import Preferences, Preferences_Dialog

class Application(Tkinter.Frame) :
	stage = db_path = None
	graphs = []
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
			self.db_path = Import(self).process(filename)
	
	def buildCanvas(self,index):
		try:
			if self.CANVAS is None:
				raise Exception('Canvas')
			if self.db_path is None:
				raise Exception('Database path')
			if self.rc is None:
				raise Exception('Run-Configuration')
		except Exception as e:
			print '[%s] is undefined' % e
			return
		self.resetCanvas()
		self.stage = self.graphs[index](self)
		self.stage.build_wrapper()
		
	def resetCanvas(self,event=None):
		try:
			if self.stage is not None:
				self.stage.destroy()
		except Exception as e:
			print 'Unable to destroy [%s]' % e
		self.CANVAS.delete('actor')
		self.CANVAS.update_idletasks()
	
	def pref_dialog(self):
		delta_configs = Preferences_Dialog(self)
		if delta_configs:
			self.CANVAS.configure(self.CANVAS,background=self.rc.get('background_color'))
			if self.stage is not None:
				self.stage.destroy()
				self.stage.build()
		
	def loadGraphs(self):
		for root, dirs, files in os.walk(os.path.join('.','graphs')):
			for fname in files:
				_name = re.match(r'^([A-Z](.*?))\.py$',fname)
				if _name is not None:
					module = __import__('graphs.%s' % _name.group(1))
					graph = module.__dict__[_name.group(1)]
					self.graphs.append(graph.Stage)
		
	def initMenu(self):
		self.MENU_BAR = Tkinter.Menu(self.master)
		self.F_MENU = Tkinter.Menu(self.MENU_BAR,tearoff=0)
		self.F_MENU.add_command(label='Open',command=self.loadFile)
		self.F_MENU.add_separator()
		self.F_MENU.add_command(label='Preferences',command=self.pref_dialog)
		self.F_MENU.add_separator()
		self.F_MENU.add_command(label='Close',command=self.resetCanvas)
		self.F_MENU.add_command(label='Quit',command=self.close)
		self.MENU_BAR.add_cascade(label='File',menu=self.F_MENU)
		self.V_MENU = Tkinter.Menu(self.MENU_BAR,tearoff=0)
		i = 0
		for graph in self.graphs:
			self.V_MENU.add_command(label=graph.MENU_TITLE,command=lambda i=i: self.buildCanvas(i))
			i+=1
		self.MENU_BAR.add_cascade(label='Views',menu=self.V_MENU)
		self.master.configure(menu=self.MENU_BAR)
		
	def initWidgets(self):
		self.loadGraphs()
		self.initMenu()
		self.VS = Tkinter.Scrollbar(self,orient='vertical')
		self.CANVAS = Tkinter.Canvas(self,background=self.rc.get('background_color'),takefocus=1,yscrollcommand=self._yset)
		self.CANVAS.pack(fill='both', expand=1, side='left')
		self.VS.config(command=self.CANVAS.yview)
		self.VS.pack(fill='y',side='right')
		self.bind('<Configure>',self._update_canvas)
		self.bind_all('<Command-Key>',self._shortCut)

	def close(self,event=None):
		self.rc.save()
		if self.db_path is not None and os.path.exists(self.db_path):
			os.remove(self.db_path)
		self.master.quit()
	
	def __init__(self,master=None):
		self.rc = Preferences()
		Tkinter.Frame.__init__(self,master,width=self.rc.get('width'),height=self.rc.get('height'))
		self.master.title('xdbug-trace-tk')
		self.pack(fill='both', expand=1)
		self.initWidgets()
		self.master.geometry(self.rc.get_geometry())
	
	def _update_canvas(self,event):
		self.rc.set_geometry(self.master.geometry())
		try:
			if self.stage is not None:
				self.stage.resize()
		except Exception:
				pass
		self.CANVAS.update_idletasks()
	
	def _shortCut(self,event):
		_c = event.char
		if _c is not None:
			if _c == 'o':
				self.loadFile()
			elif _c == 'w':
				self.resetCanvas()
			elif _c == 'q':
				self.close()
			elif _c.isdigit() and int(_c) in range(1,len(self.graphs)+1):
				self.buildCanvas(int(_c)-1)
	
	def _yset(self,start,end):
		if start == '0.0' and end == '1.0':
			self.VS.pack_forget()
		else:
			self.VS.pack(fill='y',side='right')
			self.VS.set(start,end)
		
	
if __name__ == '__main__':
	root = Tkinter.Tk()
	Application(root).mainloop()
	try:
	  root.destroy()
	except Tkinter.TclError :
		print 'Nothing to destroy'
	exit(0)