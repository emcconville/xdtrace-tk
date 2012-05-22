import sqlite3, re
import _Stage
class Stage(_Stage.Base):
	MENU_TITLE = 'Radiant Dial'
	ACTOR_TAG = 'radiant'
	def build(self):
		self.width = self.master.CANVAS.winfo_width()
		self.height = self.master.CANVAS.winfo_height()
		self.dh = sqlite3.connect(self.master.db_path)
		cursor = self.dh.cursor()
		limits_sql = 'SELECT MIN(memory_usage), MAX(memory_usage), MAX(level) FROM trace'
		self.memory_min, self.memory_max, self.total_levels = cursor.execute(limits_sql).fetchone()
		sql  = 'SELECT a.function_name, a.memory_usage AS start, b.memory_usage AS end, a.user_defined, a.level, a.function_number '
		sql += 'FROM trace a JOIN trace b ON (a.level = b.level AND a.function_number = b.function_number AND b.entry = 1) '
		sql += 'WHERE a.entry = 0 AND a.memory_usage <> b.memory_usage ORDER BY a.level ASC'
		first_level = None
		for function_name, start, end, user_defined, level, func_num in cursor.execute(sql):
			if first_level is None:
				first_level = level
			start, end = self.radiant(start,end)
			color = self.master.rc.get('primary_color' if user_defined == 1 else 'secondary_color')
			options = {
				'start'         : start,
				'extent'        : end,
				'activeoutline' : self.master.rc.get('tertiary_color'),
				'activefill'    : self.master.rc.get('tertiary_color'),
				'outline'       : color,
				'fill'          : color,
				'tags'          : ('actor',self.ACTOR_TAG,self._create_tooltip_tag(level,func_num),self._create_level_tag(level)),
				'style'         : 'arc',
				'width'         : self._offset() * 0.5
			}
			self.master.CANVAS.create_arc(self._create_bbox(level),**options)
			self.update_idletasks()
		cursor.close()
		self.master.CANVAS.tag_bind(self.ACTOR_TAG,'<Enter>',self.onMouseEnter)
		self.master.CANVAS.tag_bind(self.ACTOR_TAG,'<Leave>',self.onMouseLeave)
		self.master.CANVAS.tag_bind(self.ACTOR_TAG,'<Motion>',self.onMouseMove)
		self.master.CANVAS.tag_bind(self.ACTOR_TAG,'<Button-1>',self.onMouseClick)
		self.update_scrollregion()
		
	
	def radiant(self,start,end):
		start = int(((start - self.memory_min) / float(self.memory_max - self.memory_min)) * 360) + 90
		end   = int(((end   - self.memory_min) / float(self.memory_max - self.memory_min)) * 360) + 90
		return start, end-start
	
	def _create_bbox(self,level):
		offset = self._offset()
		scale = offset * (self.total_levels - level)
		growth = min(self.width,self.height)-scale
		padding = offset * 0.5
		return scale+padding,scale+padding,growth-padding,growth-padding
	
	def _offset(self):
		return min(self.width,self.height) / (self.total_levels * 2)
	