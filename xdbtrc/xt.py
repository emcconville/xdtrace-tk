import hashlib,os,re,sqlite3

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
