#!/usr/bin/env python

from Tkinter import *
import tkFileDialog, tkSimpleDialog
import re, os, cPickle, hashlib, sqlite3

from xdbtrc.xt import Import

class Application(Frame) :
	
	graphes = []
	
	def loadFile(self,event=None):
		foptions = {
			'title':'Please select a xDebug-Trace (.xt) File',
			'filetypes' : [('text files', '.xt'),('log files', '.xt')],
			'defaultextension' : 'xt',
			'parent' : self
		}
		filename = tkFileDialog.askopenfilename(**foptions)
		if len(filename) > 0 :
			c = Import(self.CANVAS,self.rc)
			self.db_path = c.process(filename)
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
					_name = _name.group(1)
					module = __import__("graphes.%s" % _name)
					graph = module.__dict__[_name]
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
		self.db_path = None
		self.width = 760
		self.height = 290
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

# Preferences

class Preferences:
	'''
		Simple get/set class for managing meta-data.
		Uses cPickle to load & write preferences to disk.
	'''
	attr = {
		'background_color' : '#FFFFFF',
		'base_color'       : '#2E3436',
		'neutral_color'    : '#666666',
		'primary_color'    : '#FCAF3E',
		'secondary_color'  : '#8AE234', 
		'tertiary_color'   : '#0645AD',
		'recent' : [],
	}
	def __init__(self):
		'''Generate rc filename, and load existing rc if found.'''
		self.rc = os.path.join(os.path.dirname(os.path.abspath(__file__)),__file__+'.rc')
		if os.path.exists(self.rc):
			fh = open(self.rc,'rb')
			attr = cPickle.load(fh)
			self.attr = dict(self.attr.items() + attr.items())
			fh.close()
	def save(self):
		'''Write meta-data to disk.'''
		fh = open(self.rc,'wb')
		cPickle.dump(self.attr,fh)
		fh.close()
		
	def get(self,k):
		'''Retrive attribute'''
		return self.attr[k]
	
	def set(self,k,v):
		'''Define attribute'''
		self.attr[k] = v

class Preferences_Dialog(tkSimpleDialog.Dialog):
	'''
		GUI wrapper for Preferences (rc).
		Extends tkSimpleDialog, and should be refactored;
		such that, meta-data attributes can be generated dynamically.
	'''
	def body(self,master):
		'''See tkSimpleDialog.Dialog.body'''
		Label(master,text="Graph line color").grid(row=0)
		Label(master,text="Graph selected color").grid(row=1)
		Label(master,text="Graph function color").grid(row=2)
		self.base_color = Entry(master)
		self.primary_color = Entry(master)
		self.secondary_color = Entry(master)
		self.base_color.grid(row=0,column=1)
		self.primary_color.grid(row=1,column=1)
		self.secondary_color.grid(row=2,column=1)
		self.base_color.insert(0,self.parent.rc.get('base_color'))
		self.primary_color.insert(0,self.parent.rc.get('primary_color'))
		self.secondary_color.insert(0,self.parent.rc.get('secondary_color'))
	def apply(self):
		'''See tkSimpleDialog.Dialog.apply'''
		changes = {}
		for a in ['base_color','primary_color','secondary_color']:
			e = getattr(self,a)
			v = e.get()
			if v != self.parent.rc.get(a):
				self.parent.rc.set(a,v)
				changes[a] = v
		self.result = changes.values()

def build():
	root = Tk()
	app = Application(root)
	app.mainloop()
	try:
	  root.destroy()
	except TclError :
		print "Nothing to destroy"

	exit(0)
if __name__ == '__main__':
	build()