#!/usr/bin/env python

from Tkinter import *
import tkFileDialog, tkSimpleDialog
import re, os, cPickle, hashlib, sqlite3

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
			self.clearCanvas()
			self.loadCanvas(0)
	
	def loadCanvas(self,index):
		self.clearCanvas()
		self.stage = self.graphes[index]()
		self.stage.build(self.CANVAS,self.db_path,self.rc)
		
	def clearCanvas(self,event=None):
		try:
			if self.stage is not None:
				self.stage.destroy()
		except Exception:
			pass
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
		self.F_MENU.add_command(label='Close',accelerator="Cmd+W",command=self.clearCanvas)
		self.F_MENU.add_command(label='Quit', accelerator="Cmd+Q",command=self.close)
		self.MENU_BAR.add_cascade(label='Files',menu=self.F_MENU)
		self.V_MENU = Menu(self.MENU_BAR,tearoff=0)
		i = 0
		for graph in self.graphes:
			self.V_MENU.add_command(label=graph.MENU_TITLE,command=lambda i=i: self.loadCanvas(i))
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
		self.bind_all('<Command-w>',self.clearCanvas)
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

# Graph prototype

class Stage:
	def __init__(self,canvas,config):
		self.canvas = canvas
		self.config = config
		
	def build(self):
		pass
		
	def destroy(self):
		'''Remove all bandings, and destroy all actor objects form canvas'''
		self.canvas.unbind_class('actor')
		self.canvas.delete('actor')
	
	def resize(self,width,height):
		pass

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


## Import

class Import:

	def __init__(self,canvas,rc):
		self._x = 0.0;
		self._canvas = canvas
		self._width = int(self._canvas.winfo_width() / 3.333)
		self._top   = int(self._canvas.winfo_height() / 2)
		self.database = None
		self._text = self._canvas.create_text(self._width,self._top-16,text="",tags="actor",justify="left",width=self._width,anchor="nw",fill="#CCCCCC",font="Helvetica 12")
		self._border = self._canvas.create_rectangle(self._width,self._top,self._width*2,self._top+10,fill="white",outline=rc.get('primary_color'),tags="actor")
		self._prog = self._canvas.create_rectangle(self._width,self._top,self._x,self._top+10,fill=rc.get('primary_color'),outline=rc.get('primary_color'),tags="actor")
		self._total = 0.0

	def process(self,filename):
		self.filename = filename
		self.checksum()
		if not self.exists():
			self.create_database()
			self.import_data()
		return self.database
	
	def checksum(self):
		self._canvas.itemconfig(self._text,text="Checksum...")
		md5 = hashlib.md5()
		self._total = float(os.path.getsize(self.filename))
		fh = open(self.filename)
		while True:
			data = fh.read(1024)
			if not data:
				break
			md5.update(data)
			x = float(fh.tell()) / self._total
			x -= x % 0.01
			x = int(self._width * x)
			if x is not self._x:
				self._canvas.coords(self._prog,self._width,self._top,self._width + x,self._top+10)
				self._canvas.update_idletasks()
				self._x = x
		fh.close()
		self._canvas.coords(self._prog,self._width,self._top,self._width*2,self._top+10)
		self._canvas.update_idletasks()
		self._md5 = md5.hexdigest()
		self.database = os.path.join(os.path.dirname(os.path.abspath(__file__)),'xdebug-'+self._md5+'.sqlite3')
		return self._md5
	
	def exists(self):
		return os.path.exists(self.database)
	
	def create_database(self):
		dh = sqlite3.connect(self.database)
		cursor = dh.cursor()
		cursor.execute('''CREATE TABLE meta (key text, value text)''')
		cursor.execute('''CREATE TABLE trace (
			level integer, 
			function_number integer, 
			entry integer, 
			time_index real, 
			memory_usage integer,
			function_name text,
			user_defined integer,
			owner text,
			filename text,
			line_number integer)''')
		dh.commit()
		cursor.close()
	
	def import_data(self):
		self._canvas.itemconfigure(self._text,text="Importing data...")
		self._x = 0.0
		self._canvas.coords(self._prog,self._width,self._top,self._width,self._top+10)
		dh = sqlite3.connect(self.database)
		dh.isolation_level = None 
		cursor = dh.cursor()
		fh = open(self.filename)
		for line in fh:
			x = float(fh.tell()) / self._total
			x -= x % 0.01
			x = int(self._width * x)
			if x is not self._x:
				self._canvas.coords(self._prog,self._width,self._top,self._width+x,self._top+10)
				self._canvas.update_idletasks()
				self._x = x
			info_regex = r"(^Version:\s+(?P<version>.*$)|^TRACE (?P<date_type>START|END)\s+\[(?P<date_time>.*?)\]$)"
			results = re.match(info_regex, line )
			if results is not None:
				key = value = ""
				if results.group('version') is not None:
					key = "version"
					value = results.group('version')
				else:
					key = "trace_" + results.group('date_type')
					value = results.group('date_time')
				cursor.execute('''INSERT INTO meta VALUES (?,?)''',(key,value))
				continue
			command_regex  = r"^\s*(?P<level>\d+)(?:\t|\s+)(?P<function_number>\d+)(?:\t|\s+)(?P<entry>0|1)(?:\t|\s+)(?P<time_index>\d+\.\d+)(?:\t|\s+)(?P<memory_usage>\d+)"
			command_regex += r"(?:(?:\t|\s+)(?P<function_name>[\w:_\(\)\{\}\-\.\\]+)(?:\t|\s+)(?P<user_defined>0|1)(?:(?:\t|\s+)(?P<owner>.*?))?(?:\t|\s+)(?P<filename>.*?)(?:\t|\s+)(?P<line_number>\d+))?$"
			results = re.match(command_regex,line)
			if results is not None:
				cursor.execute('''INSERT INTO trace VALUES (?,?,?,?,?,?,?,?,?,?)''',results.groups())
				continue
		self._canvas.coords(self._prog,self._width,self._top,self._width*2,self._top+10)
		self._canvas.update_idletasks()
		cursor.close()

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