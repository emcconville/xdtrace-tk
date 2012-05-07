MENU_TITLE = 'Pie Chart'
class Stage():
	def build(self,canvas,db_path,config):
		'''Render graph from database'''
		self.canvas = canvas
		self.db_path = db_path
		self.config = config
		print 'building'
		return
		
	def destroy(self):
		'''Remove all bandings, and destroy all actor objects form canvas'''
		print 'destroying'
		self.canvas.unbind_class('actor')
		self.canvas.delete('actor')
		return
		
	def resize(self,width,height):
		'''Rebuild graph on canvas w/h change'''
		print 'Resize to %dx%d' % (width,height)
		return