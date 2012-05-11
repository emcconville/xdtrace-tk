import sqlite3, math
class Stage():
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
		sql += 'WHERE a.entry = 0 AND a.memory_usage <> b.memory_usage ORDER BY a.level DESC'
		offset_x = self.width  / self.total_levels
		offset_y = self.height / self.total_levels
		for function_name, start, end, user_defined, level in cursor.execute(sql):
			print function_name, start, end, user_defined, level
			start, end = self.radiant(start,end)
			top, height = (self.total_levels - level) * offset_y + 20, self.height - (offset_y * (self.total_levels - level)) -20
			left, width = (self.total_levels - level) * offset_x + 20, self.width  - (offset_x * (self.total_levels - level)) -20
			print start, end, level
			pos = left,top,width,height
			color = self.config.get('primary_color' if user_defined == 1 else 'secondary_color')
			level_tag = 'level%s' % str(level)
			p = self.canvas.create_arc(pos,start=start,extent=end,fill=color,tags=('actor','radiant',level_tag))
			#self.canvas.lift(level_tag,aboveThis='level%s' % str(int(level)+1))
		
	def destroy(self):
		pass
	def resize(self,width,height):
		pass
	
	def radiant(self,start,end):
		start = math.floor(((start - self.memory_min) / float(self.memory_max - self.memory_min)) * 360)
		end   = math.floor(((end   - self.memory_min) / float(self.memory_max - self.memory_min)) * 360)
		print start, end-start
		return start, end-start