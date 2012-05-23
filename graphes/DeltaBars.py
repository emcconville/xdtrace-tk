import sqlite3
import _Stage
class Stage(_Stage.Base):
	MENU_TITLE = 'Delta Bars'
	ACTOR_TAG = 'bar'
	def build(self):
		self.width = self.master.CANVAS.winfo_width() - 40
		dh = sqlite3.connect(self.master.db_path)
		cursor = dh.cursor()
		limits_sql = 'SELECT MIN(memory_usage), MAX(memory_usage), MAX(level) FROM trace'
		self.min_memory,self.max_memory, self.max_level = cursor.execute(limits_sql).fetchone()
		self.total_memory = float(self.max_memory - self.min_memory)
		sql  = '''SELECT 
									a.function_name, a.memory_usage AS memory_start, b.memory_usage AS memory_end, 
									a.user_defined, a.level, a.function_number 
							FROM trace a JOIN trace b 
								ON (a.level = b.level AND a.function_number = b.function_number AND b.entry = 1) 
							WHERE a.entry = 0'''
		for function_name, memory_start, memory_end, user_defined, level, function_number in cursor.execute(sql):
			color = self.master.rc.get("primary_color" if user_defined > 0 else "secondary_color")
			opts = {
				'fill'    : color, 
				'outline' : self.master.rc.get('neutral_color'),
				'tags'    : ("actor",self.ACTOR_TAG,self._create_tooltip_tag(level,function_number))
			}
			self.master.CANVAS.create_rectangle(self._create_bbox(level,memory_start,memory_end), **opts)
			self.update_idletasks()
		self.master.CANVAS.tag_bind(self.ACTOR_TAG,'<Enter>',self.onMouseEnter)
		self.master.CANVAS.tag_bind(self.ACTOR_TAG,'<Leave>',self.onMouseLeave)
		self.master.CANVAS.tag_bind(self.ACTOR_TAG,'<Motion>',self.onMouseMove)
		self.update_scrollregion()
		
	def _create_bbox(self,level,memory_start,memory_end):
		left = int(((memory_start-self.min_memory) / self.total_memory) * self.width) + 20
		width = int(((memory_end-self.min_memory) / self.total_memory) * self.width) + 20
		top = int(level) * 20
		return left,top,width,top+18