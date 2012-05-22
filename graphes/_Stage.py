import re,sqlite3

class Base:
	_tto = 5
	def __init__(self,master):
		self.master = master
	def build(self): pass
	def destroy(self):
		self.master.CANVAS.delete('actor')
		self.master.CANVAS.update_idletasks()
	
	def resize(self): pass
	def onMouseClick(self,event): pass
	def onMouseEnter(self,event): 
		current = self._find_id_tag()
		if current is not None:
			args = {
				'level' : current['level'],
				'function_number' : current['function_number'],
				'x' : self.master.CANVAS.canvasx(event.x),
				'y' : self.master.CANVAS.canvasy(event.y)
			}
			self.showToolTip(**args)
	
	def onMouseMove(self,event):
		self.moveToolTip(x=self.master.CANVAS.canvasx(event.x),y=self.master.CANVAS.canvasy(event.y))
	
	def onMouseLeave(self,event):
		self.hideToolTip()
	
	def showToolTip(self,**args):
		message, self._ttw, self._tth = self.getInfo(args['level'],args['function_number'])
		self._tto = 5
		bb = args['x']+self._tto,args['y']+self._tto,args['x']+self._ttw+self._tto,args['y']+self._tth+self._tto
		_x,_y = map(lambda x: int(x)+int(self._tto), bb[:2])
		self.master.CANVAS.coords('tooltip',bb)
		self.master.CANVAS.coords('tooltext',_x,_y)
		self.master.CANVAS.update_idletasks()
		self.master.CANVAS.itemconfig('tooltip',fill=self.master.rc.get('background_color'),outline=self.master.rc.get('neutral_color'))
		self.master.CANVAS.itemconfig('tooltext',fill=self.master.rc.get('base_color'),text=message)
		self.master.CANVAS.update_idletasks()

	def moveToolTip(self,**args):
		self.master.CANVAS.update_idletasks()
		bb = args['x']+self._tto,args['y']+self._tto,args['x']+self._ttw+self._tto,args['y']+self._tth+self._tto
		_x,_y = map(lambda x: int(x)+int(self._tto), bb[:2])
		self.master.CANVAS.coords('tooltip',bb)
		self.master.CANVAS.coords('tooltext',_x,_y)
		self.master.CANVAS.update_idletasks()

	def hideToolTip(self):
		self.master.CANVAS.coords('tooltip',0,0,0,0)
		self.master.CANVAS.itemconfig('tooltip',fill='',outline='')
		self.master.CANVAS.coords('tooltext',0,0)
		self.master.CANVAS.itemconfig('tooltext',fill='')
		self.master.CANVAS.update_idletasks()

	def getInfo(self,level,function_number):
		dh = sqlite3.connect(self.master.db_path)
		cursor = dh.cursor()
		sql = '''
			SELECT 
				a.function_name,
				a.filename,
				a.line_number,
				b.memory_usage - a.memory_usage AS memory_usage,
				b.time_index - a.time_index AS time_index
			FROM trace a 
				JOIN trace b 
					ON (a.level = b.level AND a.function_number = b.function_number AND b.entry = 1)
			WHERE 
				a.level = %d 
				AND a.function_number = %d 
		''' % (int(level),int(function_number))
		function_name,filename,line_number,memory_usage,time_index = cursor.execute(sql).fetchone()
		cursor.close()
		data = [
			'Function: %s' % function_name,
			'Memory: %.4fkb' % (memory_usage / 1024.0),
			'Time: %.4fms' % time_index
		]
		height = len(data) * 17;
		width = 0;
		for _n in data:
			if len(_n) > width:
				width = len(_n)+1
		return '\n'.join(data), width * 6, height
	
	def _find_id_tag(self,tagorid="current"):
		for tag in self.master.CANVAS.gettags(tagorid):
			results = re.match(r'tt(?P<level>\d+)-(?P<func_num>\d+)',tag)
			if results is not None:
				return {'level' : results.group('level'),'function_number' : results.group('func_num')}
		return None
	
	def _create_tooltip_tag(self,level,function_number):
		return 'tt%s-%s' % (str(level),str(function_number))
	
	def _create_level_tag(self,level):
		return 'l%s' % str(level)