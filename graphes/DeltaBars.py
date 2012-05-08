import sqlite3
class Stage():
	MENU_TITLE = 'Delta Bars'
	def build(self,canvas,db_path,config):
		dh = sqlite3.connect(db_path)
		cursor = dh.cursor()
		sql = 'SELECT a.function_name, (b.memory_usage - a.memory_usage) AS memory_delta, (ROUND(b.time_index,5) - ROUND(a.time_index,5)) AS time_delta FROM trace a JOIN trace b ON (a.level = b.level AND a.function_number = b.function_number AND b.entry = 1) WHERE a.entry = 0'
		for row in cursor.execute(sql):
			print row
		
	def destroy(self):
		pass
	def resize(self,width,height):
		pass