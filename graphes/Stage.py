import abc

class Stage(object):
	__metaclass__ = abc.ABCMeta
	
	@abc.abstractmethod
	def build(self,canvas,db_path,config):
		'''Render graph from database'''
		return
		
	@abc.abstractmethod
	def destroy(self):
		'''Remove all bandings, and destroy all actor objects form canvas'''
		#self.canvas.unbind_class('actor')
		#self.canvas.delete('actor')
		return
		
	@abc.abstractmethod
	def resize(self,width,height):
		'''Rebuild graph on canvas w/h change'''
		return

