#!/usr/bin/env python
from Tkinter import *
#from .Trace import *
import tkFileDialog, tkSimpleDialog
import os, cPickle, hashlib, sqlite3

class Application(Frame) :
	def loadFile(self):
		foptions = {
			'title':'Please select a xDebug-Trace (.xt) File',
			'filetypes' : [('text files', '.xt'),('log files', '.xt')],
			'defaultextension' : 'xt',
			'parent' : self
		}
		filename = tkFileDialog.askopenfilename(**foptions)
		if len(filename) > 0 :
			c = Import(self.CANVAS,self.rc)
			md5 = c.process(filename)
			#self.wait_window(c.top)
			print md5
			#self.Trace = Trace(filename)
			#self.buildTraces()
	
	def closeTrace(self):
		if not len(self.Trace.traces):
			raise 'No traces to clear'
			return
		for i in self.Trace.traces:
			try:
				self.CANVAS.delete('_'+i['_id'])
			except Exception:
				pass
	
	def buildTraces(self):
		if not len(self.Trace.traces):
			raise 'No traces to builde'
			return
		self._buildTracesCanvas()
			
	def _buildTracesCanvas(self):
		l = len(self.Trace.traces)
		prev_x = 20
		prev_y = 270
		for i in range(0,l,1):
			x,y    = self.Trace.getPoint(i)
			next_x = int(700 * x) + 20;
			next_y = 250 - int(250 * y) + 20
			if next_x is not prev_x and next_y is not prev_y:
				self.CANVAS.create_line(prev_x,prev_y,next_x,next_y, fill=self.rc.get('c_line'), width=3, tags=(self.Trace.traces[i]['function'],'_'+str(self.Trace.traces[i]['_id'])))
				prev_x = next_x
				prev_y = next_y
		
	def pref_dialog(self):
		d = Preferences_Dialog(self)
		
	def initMenu(self):
		self.MENU_BAR = Menu(self.master)
		self.F_MENU = Menu(self.MENU_BAR,tearoff=0)
		self.F_MENU.add_command(label='Open',command=self.loadFile)
		self.F_MENU.add_separator()
		self.F_MENU.add_command(label='Preferences',command=self.pref_dialog)
		self.F_MENU.add_separator()
		self.F_MENU.add_command(label='Close',command=self.closeTrace)
		self.F_MENU.add_command(label='Exit',command=self.close)
		self.MENU_BAR.add_cascade(label='Files',menu=self.F_MENU)
		self.master.config(menu=self.MENU_BAR)
		
	def initWidgets(self):
		self.initMenu()
		self.CANVAS = Canvas(self,width=self['width'],height=self['height'])
		self.CANVAS.pack(fill='both', expand=1)
		self._border = self.CANVAS.create_rectangle(20,20,self.width-20,self.height-20,fill='white',width=1,outline='#cccccc')
		self.bind('<Configure>',self._update_canvas)
		
	def close(self):
		self.rc.save()
		self.master.quit()
	
	def __init__(self,master=None):
		self.rc = Preferences()
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
		self.rc = os.path.join(os.path.dirname(os.path.abspath(__file__)),'.xdtrace_rc')
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
		self.database = None
		self._prog = self._canvas.create_rectangle(0,0,self._x,10,fill=rc.get('c_selected'))
		self._total = 0.0

	def process(self,filename):
		self.filename = filename
		self.checksum()
		if not self.exists():
			self.create_database()
		return self.database
	
	def checksum(self):
		md5 = hashlib.md5()
		self._total = float(os.path.getsize(self.filename))
		fh = open(filename)
		while True:
			data = fh.read(1024)
			if not data:
				break
			md5.update(data)
			x = float(fh.tell()) / self._total
			x -= x % 0.01
			x = int(300 * x)
			if x <> self._x:
				self._canvas.coords(self._prog,0,0,x,10)
				#self._canvas.update_idletasks()
				self._x = x
		fh.close()
		self._md5 = md5.hexdigest()
		self.database = os.path.join(os.path.dirname(os.path.abspath(__file__)),self._md5+'.sqlite3')
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
		cursor.commit()
		cursor.close()
		

def demo():
	root = Tk()
	app = Application(root)
	app.mainloop()
	try:
	  root.destroy()
	except TclError :
		print "Nothing to destroy"

	exit(0)
if __name__ == '__main__':
	demo()