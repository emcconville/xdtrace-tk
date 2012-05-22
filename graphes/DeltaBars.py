import sqlite3
import _Stage
class Stage(_Stage.Base):
	MENU_TITLE = 'Delta Bars'
	def build(self):
		self.width = self.master.CANVAS.winfo_width() - 40
		dh = sqlite3.connect(self.master.db_path)
		cursor = dh.cursor()
		limits_sql = 'SELECT MIN(memory_usage), MAX(memory_usage), MAX(level) FROM trace'
		self.min_memory,self.max_memory, self.max_level = cursor.execute(limits_sql).fetchone()
		self.total_memory = float(self.max_memory - self.min_memory)
		sql  = 'SELECT a.function_name, a.memory_usage AS memory_start, b.memory_usage AS memory_end, a.user_defined, a.level, a.function_number '
		sql += 'FROM trace a JOIN trace b ON (a.level = b.level AND a.function_number = b.function_number AND b.entry = 1) '
		sql += 'WHERE a.entry = 0 AND memory_start <> memory_end'
		for function_name, memory_start, memory_end, user_defined, level, function_number in cursor.execute(sql):
			left = int(((memory_start-self.min_memory) / self.total_memory) * self.width) + 20
			width = int(((memory_end-self.min_memory) / self.total_memory) * self.width) + 20
			color = self.master.rc.get("primary_color" if user_defined > 0 else "secondary_color")
			top = int(level) * 21 + 20
			bb = left,top,width,top+20
			opts = {
				'fill'    : color, 
				'outline' : 'white',
				'tags'    : ("actor",'bar',self._create_tooltip_tag(level,function_number))
			}
			self.master.CANVAS.create_rectangle(bb, **opts)
		self.master.CANVAS.config(scrollregion=(0,0)+self.master.CANVAS.bbox('all')[2:])
		self.master.CANVAS.tag_bind('bar','<Enter>',self.onMouseEnter)
		self.master.CANVAS.tag_bind('bar','<Leave>',self.onMouseLeave)
		self.master.CANVAS.tag_bind('bar','<Motion>',self.onMouseMove)
		self.master.CANVAS.create_rectangle(0,0,100,100,fill='',outline='',tags=('actor','tooltip'))
		self.master.CANVAS.create_text(10,10,fill='',text='',anchor='nw',tags=('actor','tooltext'),font='Helvetica 12')
