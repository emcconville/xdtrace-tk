import sqlite3, math, re

class Stage(object):
	MENU_TITLE = 'Radiant Dial'
	
	def build(self,canvas,db_path,config):
		self.canvas = canvas
		self.config = config
		self.width = self.canvas.winfo_width()
		self.height = self.canvas.winfo_height()
		self.dh = sqlite3.connect(db_path)
		cursor = self.dh.cursor()
		limits_sql = 'SELECT MIN(memory_usage), MAX(memory_usage), MAX(level) FROM trace'
		self.memory_min, self.memory_max, self.total_levels = cursor.execute(limits_sql).fetchone()
		sql  = 'SELECT a.function_name, a.memory_usage AS start, b.memory_usage AS end, a.user_defined, a.level, a.function_number '
		sql += 'FROM trace a JOIN trace b ON (a.level = b.level AND a.function_number = b.function_number AND b.entry = 1) '
		sql += 'WHERE a.entry = 0 AND a.memory_usage <> b.memory_usage ORDER BY a.level ASC'
		offset = (self.width if self.width < self.height else self.height) / (self.total_levels * 2)
		first_level = None
		for function_name, start, end, user_defined, level, func_num in cursor.execute(sql):
			if first_level is None:
				first_level = level
			start, end = self.radiant(start,end)
			scale = offset * (self.total_levels - level)
			growth = self.width-scale
			padding = offset * 0.5
			pos = scale+padding,scale+padding,growth-padding,growth-padding
			color = self.config.get('primary_color' if user_defined == 1 else 'secondary_color')
			options = {
				'start'         : start,
				'extent'        : end,
				'activeoutline' : self.config.get('tertiary_color'),
				'activefill'    : self.config.get('tertiary_color'),
				'outline'       : color,
				'fill'          : color,
				'tags'          : ('actor','radiant','r%s-%s' % (level,func_num),'level%s' % str(level)),
				'style'         : 'arc',
				'width'         : offset * 0.5
			}
			self.canvas.create_arc(pos,**options)
			self.canvas.update_idletasks()
		cursor.close()
		for _x in range(self.total_levels,0):
			self.canvas.tag_raise('level%s' % _x)
		self.canvas.tag_bind('radiant','<Enter>',self.onMouseEnter)
		self.canvas.tag_bind('radiant','<Leave>',self.onMouseLeave)
		self.canvas.tag_bind('radiant','<Motion>',self.onMouseMove)
		self.canvas.tag_bind('radiant','<Button-1>',self.onMouseClick)
		self.canvas.create_rectangle(0,0,100,100,fill='',outline='',tags=('actor','tooltip'))
		self.canvas.create_text(10,10,fill='',text='',anchor='nw',tags=('actor','tooltext'),font='Helvetica 12')
		
	def destroy(self):
		self.canvas.delete('actor')
		self.canvas.update_idletasks()

	def resize(self,width,height):
		pass
	
	def onMouseClick(self,event):
		pass

	def onMouseEnter(self,event):
		for tag in self.canvas.gettags('current'):
			results = re.match(r'r(?P<level>\d+)-(?P<func_num>\d+)',tag)
			if results is not None:
				args = {
					'level' : results.group('level'),
					'function_number' : results.group('func_num'),
					'x' : event.x,
					'y' : event.y
				}
				self.showToolTip(**args)

	def onMouseLeave(self,event):
		self.hideToolTip()

	def onMouseMove(self,event):
		self.moveToolTip(x=event.x,y=event.y)
	
	def radiant(self,start,end):
		start = math.floor(((start - self.memory_min) / float(self.memory_max - self.memory_min)) * 360)
		end   = math.floor(((end   - self.memory_min) / float(self.memory_max - self.memory_min)) * 360)
		return start, end-start
		
	def showToolTip(self,**args):
		message, self._ttw, self._tth = self.getInfo(args['level'],args['function_number'])
		self._tto = 5
		bb = args['x']+self._tto,args['y']+self._tto,args['x']+self._ttw+self._tto,args['y']+self._tth+self._tto
		_x,_y = map(lambda x: int(x)+int(self._tto), bb[:2])
		self.canvas.coords('tooltip',bb)
		self.canvas.coords('tooltext',_x,_y)
		self.canvas.update_idletasks()
		self.canvas.itemconfig('tooltip',fill=self.config.get('background_color'),outline=self.config.get('neutral_color'))
		self.canvas.itemconfig('tooltext',fill=self.config.get('base_color'),text=message)
		self.canvas.update_idletasks()
	
	def moveToolTip(self,**args):
		self.canvas.update_idletasks()
		bb = args['x']+self._tto,args['y']+self._tto,args['x']+self._ttw+self._tto,args['y']+self._tth+self._tto
		_x,_y = map(lambda x: int(x)+int(self._tto), bb[:2])
		self.canvas.coords('tooltip',bb)
		self.canvas.coords('tooltext',_x,_y)
		self.canvas.update_idletasks()
	
	def hideToolTip(self):
		self.canvas.coords('tooltip',0,0,0,0)
		self.canvas.itemconfig('tooltip',fill='',outline='')
		self.canvas.coords('tooltext',0,0)
		self.canvas.itemconfig('tooltext',fill='')
		self.canvas.update_idletasks()
	
	def getInfo(self,level,function_number):
		cursor = self.dh.cursor()
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