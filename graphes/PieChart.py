import abc
from Stage import Stage

class PieChart(Stage):
		
	def build(self,canvas,db_path,config):
		'''Render graph from database'''
		return
		
	def destroy(self):
		'''Remove all bandings, and destroy all actor objects form canvas'''
		self.canvas.unbind_class('actor')
		self.canvas.delete('actor')
		return
		
	def resize(self,width,height):
		'''Rebuild graph on canvas w/h change'''
		return

Stage.register(PieChart)

if __name__ == '__main__':
	print 'Subclass:', issubclass(PieChart, Stage)
	print 'Instance:', isinstance(PieChart(), Stage)