MENU_TITLE = 'Pie Chart'
class Stage():
	def build(self):
		'''Render graph from database'''
		print 'Clicked'
		return
		
	def destroy(self):
		'''Remove all bandings, and destroy all actor objects form canvas'''
		self.canvas.unbind_class('actor')
		self.canvas.delete('actor')
		return
		
	def resize(self,width,height):
		'''Rebuild graph on canvas w/h change'''
		return