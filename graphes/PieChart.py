import sqlite3
class Stage(object):
	MENU_TITLE = 'Pie Chart'
	def build(self,canvas,db_path,config):
		'''Render graph from database'''
		self.canvas = canvas
		self.db_path = db_path
		self.config = config
		width = self.canvas.winfo_width()
		height = self.canvas.winfo_height()
		center_x = width / 2
		center_y = height / 2
		dh = sqlite3.connect(self.db_path)
		cursor = dh.cursor()
		sql = 'SELECT COUNT(user_defined), user_defined FROM trace WHERE entry = 0 GROUP BY user_defined'
		pie_data = {'system': 0, 'user': 0}
		for row in cursor.execute(sql):
			if int(row[1]) == 0:
				pie_data['system'] += row[0]
			else:
				pie_data['user'] += row[0]
		cursor.close()
		mx = float(sum(pie_data.values()))
		switch = 360-int(360 * (pie_data['system']/mx))
		pos = 40,40,width-40,height-40
		self._system = self.canvas.create_arc(pos,start=0,extent=switch,fill=self.config.get('primary_color'),outline=self.config.get('primary_color'),tags="actor")
		pos = 40,40,width-40,height-40
		self._user = self.canvas.create_arc(pos,start=switch,extent=360-switch,fill=self.config.get('secondary_color'),outline=self.config.get('secondary_color'),tags="actor")
		return
		
	def destroy(self):
		'''Remove all bandings, and destroy all actor objects form canvas'''
		self.canvas.delete(self._system)
		self.canvas.delete(self._user)
		return
		
	def resize(self,width,height):
		'''Rebuild graph on canvas w/h change'''
		#print "Resizing %dx%d" % (width,height)
		self.canvas.coords(self._system,40,40,width-40,height-40)
		self.canvas.coords(self._user,40,40,width-40,height-40)
		return

		