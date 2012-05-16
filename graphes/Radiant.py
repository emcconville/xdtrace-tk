import sqlite3, math
class Stage(object):
	MENU_TITLE = 'Radiant Dial'
	
	def build(self,canvas,db_path,config):
		self.canvas = canvas
		self.config = config
		self.width = self.canvas.winfo_width()
		self.height = self.canvas.winfo_height()
		dh = sqlite3.connect(db_path)
		cursor = dh.cursor()
		limits_sql = 'SELECT MIN(memory_usage), MAX(memory_usage), MAX(level) FROM trace'
		self.memory_min, self.memory_max, self.total_levels = cursor.execute(limits_sql).fetchone()
		sql  = 'SELECT a.function_name, a.memory_usage AS start, b.memory_usage AS end, a.user_defined, a.level '
		sql += 'FROM trace a JOIN trace b ON (a.level = b.level AND a.function_number = b.function_number AND b.entry = 1) '
		sql += 'WHERE a.entry = 0 AND a.memory_usage <> b.memory_usage ORDER BY a.level ASC'
		offset = self.width  / (self.total_levels * 2)
		first_level = None
		for function_name, start, end, user_defined, level in cursor.execute(sql):
			if first_level is None:
				first_level = level
			padding = (offset/2) if first_level == level else (offset)
			start, end = self.radiant(start,end)
			scale = offset * (self.total_levels - level)
			growth = self.width-scale
			pos = scale+padding,scale+padding,growth-padding,growth-padding
			color = self.config.get('primary_color' if user_defined == 1 else 'secondary_color')
			level_tag = 'level%s' % str(level)
			options = {
				'start'         : start,
				'extent'        : end,
				'activeoutline' : self.config.get('tertiary_color'),
				'activefill'    : self.config.get('tertiary_color'),
				'outline'       : self.config.get('background_color') if level is first_level else color,
				'fill'          : color,
				'tags'          : ('actor','radiant',level_tag),
				'style'         : 'pieslice' if level == first_level else 'arc',
				'width'         : 1 if level == first_level else (padding/2)
			}
			self.canvas.create_rectangle(pos,tags="actor")
			self.canvas.create_text(pos[2],pos[3],tags="actor",text=level)
			self.canvas.create_arc(pos,**options)
			self.canvas.update_idletasks()
		cursor.close()
		for _x in range(self.total_levels,0):
			self.canvas.tag_raise('level%s' % _x)
		self.canvas.tag_bind('radiant',"<Enter>",self.onMouseEnter)
		self.canvas.tag_bind('radiant',"<Leave>",self.onMouseLeave)
		self.canvas.tag_bind('radiant',"<Motion>",self.onMouseMove)
		self.canvas.tag_bind('radiant',"<Button-1>",self.onMouseClick)
		
	def destroy(self):
		self.canvas.delete('actor')
		self.canvas.update_idletasks()

	def resize(self,width,height):
		pass
	
	def onMouseClick(self,event):
		print event.widget

	def onMouseEnter(self,event):
		print event.type

	def onMouseLeave(self,event):
		print event.type

	def onMouseMove(self,event):
		print event.x,event.y
	
	def radiant(self,start,end):
		start = math.floor(((start - self.memory_min) / float(self.memory_max - self.memory_min)) * 360)
		end   = math.floor(((end   - self.memory_min) / float(self.memory_max - self.memory_min)) * 360)
		return start, end-start