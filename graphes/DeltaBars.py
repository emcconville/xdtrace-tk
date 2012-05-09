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
		limits_sql = 'SELECT MIN(memory_usage), CAST(MAX(memory_usage) AS FLOAT) FROM trace'
		self.min_memory,self.max_memory = cursor.execute(limits_sql).fetchone()
		sql = 'SELECT a.function_name, a.memory_usage AS memory_start, (b.memory_usage - a.memory_usage) AS memory_delta FROM trace a JOIN trace b ON (a.level = b.level AND a.function_number = b.function_number AND b.entry = 1) WHERE a.entry = 0'
		i = 0;
		for function_name, memory_start, memory_delta in cursor.execute(sql):
			i = i+1
			left = 40
			top = left * i
			height = 20
			width = self.width
			self.canvas.create_rectangle(left,top,width,top+height, fill=self.config.get("background_color"), outline=self.config.get("primary_color"))
			print function_name, memory_start, memory_delta
		
	def destroy(self):
		pass
	def resize(self,width,height):
		pass