#!/usr/bin/env python

from Tkinter import *
import tkFileDialog, tkSimpleDialog
import re, os, cPickle, hashlib, sqlite3

class Application(Frame) :
	
	def showPieChart(self):
		width = self.CANVAS.winfo_width()
		height = self.CANVAS.winfo_height()
		center_x = width / 2
		center_y = height / 2
		dh = sqlite3.connect(self.db_path)
		cursor = dh.cursor()
		sql = 'SELECT COUNT(user_defined), user_defined FROM trace WHERE entry = 0 GROUP BY user_defined'
		pie_data = {'system': 0, 'user': 0}
		for row in cursor.execute(sql):
			if int(row[1]) == 0:
				pie_data['system'] += row[0]
			else:
				pie_data['user'] += row[0]
		cursor.close()
		mx = float(sum(pie_data.values()))
		switch = 360-int(360 * (pie_data['system']/mx))
		pos = 45,40,width-40,height-45
		self.CANVAS.create_arc(pos,start=0,extent=switch,fill=self.rc.get('c_selected'),outline=self.rc.get('c_selected'),tag="actor")
		pos = 40,45,width-45,height-40
		self.CANVAS.create_arc(pos,start=switch,extent=360-switch,fill=self.rc.get('c_other'),outline=self.rc.get('c_other'),tag="actor")
	
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
			self.showPieChart()
	
	def clearCanvas(self,event=None):
		try:
			self.CANVAS.delete('actor')
		except Exception:
			pass
	
	def pref_dialog(self):
		d = Preferences_Dialog(self)
		
	def initMenu(self):
		self.MENU_BAR = Menu(self.master)
		self.F_MENU = Menu(self.MENU_BAR,tearoff=0)
		self.F_MENU.add_command(label='Open',accelerator="Cmd+O",command=self.loadFile)
		self.F_MENU.add_separator()
		self.F_MENU.add_command(label='Preferences',command=self.pref_dialog)
		self.F_MENU.add_separator()
		self.F_MENU.add_command(label='Close',accelerator="Cmd+W",command=self.clearCanvas)
		self.F_MENU.add_command(label='Exit',accelerator=	"Cmd+Q",command=self.close)
		self.MENU_BAR.add_cascade(label='Files',menu=self.F_MENU)
		self.master.config(menu=self.MENU_BAR)
		
	def initWidgets(self):
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
		if os.path.exists(self.db_path):
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
		self.CANVAS.update_idletasks()



# Preferences

class Preferences:
	attr = {
		'c_selected' : '#FCAF3E',
		'c_line' : '#2E3436',
		'c_other': '#8AE234', 
		'recent' : [],
	}
	def __init__(self):
		self.rc = os.path.join(os.path.dirname(os.path.abspath(__file__)),__file__+'.rc')
		if os.path.exists(self.rc):
			fh = open(self.rc,'rb')
			attr = cPickle.load(fh)
			self.attr = dict(self.attr.items() + attr.items())
			fh.close()
	def save(self):
		fh = open(self.rc,'wb')
		cPickle.dump(self.attr,fh)
		fh.close()
		
	def get(self,k):
		return self.attr[k]
	
	def set(self,k,v):
		self.attr[k] = v

class Preferences_Dialog(tkSimpleDialog.Dialog):
	def body(self,master):
		Label(master,text="Graph line color").grid(row=0)
		Label(master,text="Graph selected color").grid(row=1)
		Label(master,text="Graph function color").grid(row=2)
		self.c_line = Entry(master)
		self.c_selected = Entry(master)
		self.c_other = Entry(master)
		self.c_line.grid(row=0,column=1)
		self.c_selected.grid(row=1,column=1)
		self.c_other.grid(row=2,column=1)
		self.c_line.insert(0,self.parent.rc.get('c_line'))
		self.c_selected.insert(0,self.parent.rc.get('c_selected'))
		self.c_other.insert(0,self.parent.rc.get('c_other'))
	def apply(self):
		changes = {}
		for a in['c_line','c_selected','c_other']:
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
		self._text = self._canvas.create_text(self._width,self._top-16,text="",tag="actor",justify="left",width=self._width,anchor="nw",fill="#CCCCCC",font="Helvetica 12")
		self._border = self._canvas.create_rectangle(self._width,self._top,self._width*2,self._top+10,fill="white",outline=rc.get('c_selected'),tag="actor")
		self._prog = self._canvas.create_rectangle(self._width,self._top,self._x,self._top+10,fill=rc.get('c_selected'),outline=rc.get('c_selected'),tag="actor")
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
			if x <> self._x:
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
			if x <> self._x:
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