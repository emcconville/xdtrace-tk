import sqlite3
class Stage(object):
	MENU_TITLE = 'Delta Bars'
	def build(self,canvas,db_path,config):
		self.canvas = canvas
		self.config = config
		self.width = self.canvas.winfo_width() - 40
		dh = sqlite3.connect(db_path)
		cursor = dh.cursor()
		limits_sql = 'SELECT MIN(memory_usage), MAX(memory_usage), MAX(level) FROM trace'
		self.min_memory,self.max_memory, self.max_level = cursor.execute(limits_sql).fetchone()
		self.total_memory = float(self.max_memory - self.min_memory)
		self.lefts = []
		self.past_level = 0
		for _x in range(0,self.max_level):
			self.lefts.append(40)
		sql  = 'SELECT a.function_name, (b.memory_usage - a.memory_usage) AS memory_delta, a.user_defined, a.level '
		sql += 'FROM trace a JOIN trace b ON (a.level = b.level AND a.function_number = b.function_number AND b.entry = 1) '
		sql += 'WHERE a.entry = 0 AND memory_delta <> 0'
		top = 40
		for function_name, memory_delta, user_defined, level in cursor.execute(sql):
			left = self.getLeft(level)
			width = left + int((memory_delta / self.total_memory) * self.width)
			color = self.config.get("primary_color" if user_defined > 0 else "secondary_color")
			self.canvas.create_rectangle(left,top,width,top+10, fill=color, outline=color,tags=("actor"))
			info = "%s %c%d [%d]" % (function_name,'+' if memory_delta > 0 else '-' , memory_delta,level)
			self.canvas.create_text(width+10,top,text=info,fill=self.config.get('neutral_color'),tags="actor",anchor="nw",font="Helvetica 9")
			self.lefts[level-1] = width
			top += 10

		
	def destroy(self):
		pass
	def resize(self,width,height):
		pass
	
	def getLeft(self,level):
		level = level-1
		if level > self.past_level:
			for _x in range(level,len(self.lefts)):
				self.lefts[_x] = self.lefts[level]
		return self.lefts[level]