import sqlite3
class Stage():
	MENU_TITLE = 'Delta Bars'
	def build(self,canvas,db_path,config):
		self.canvas = canvas
		self.config = config
		self.width = self.canvas.winfo_width() - 40
		self.height = self.canvas.winfo_height() - 40
		dh = sqlite3.connect(db_path)
		cursor = dh.cursor()
		limits_sql = 'SELECT MIN(memory_usage), MAX(memory_usage) FROM trace'
		self.min_memory,self.max_memory = cursor.execute(limits_sql).fetchone()
		self.total_memory = float(self.max_memory - self.min_memory)
		sql  = 'SELECT a.function_name, (b.memory_usage - a.memory_usage) AS memory_delta, a.user_defined '
		sql += 'FROM trace a JOIN trace b ON (a.level = b.level AND a.function_number = b.function_number AND b.entry = 1) '
		sql += 'WHERE a.entry = 0 AND memory_delta <> 0'
		left = 40;
		top = 40
		for function_name, memory_delta, user_defined in cursor.execute(sql):
			width = left + int((memory_delta / self.total_memory) * self.width)
			color = self.config.get("primary_color" if user_defined > 0 else "secondary_color")
			self.canvas.create_rectangle(left,top,width,top+10, fill=color, outline=color,tags=("actor"))
			info = "%s %c%d" % (function_name,'+' if memory_delta > 0 else '-' , memory_delta)
			self.canvas.create_text(width+10,top,text=info,fill=self.config.get('neutral_color'),tags="actor",anchor="nw",font="Helvetica 9")
			left = width
			top += 10

		
	def destroy(self):
		pass
	def resize(self,width,height):
		pass