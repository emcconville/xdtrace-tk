
from Tkinter import *
import tkFileDialog, tkSimpleDialog
import os, cPickle

# Preferences

class Preferences:
	'''
		Simple get/set class for managing meta-data.
		Uses cPickle to load & write preferences to disk.
	'''
	attr = {
		'background_color' : '#FFFFFF',
		'base_color'       : '#2E3436',
		'neutral_color'    : '#666666',
		'primary_color'    : '#FCAF3E',
		'secondary_color'  : '#8AE234', 
		'tertiary_color'   : '#0645AD',
		'recent' : [],
		'root_x' : 0,
		'root_y' : 0,
		'height' : 360,
		'width'  : 760,
	}
	def __init__(self):
		'''Generate rc filename, and load existing rc if found.'''
		
		# Create private copy of defaults
		self._attr = self.attr
		
		# Look for, and load, previous rc
		self.rc = os.path.join(os.path.dirname(os.path.abspath(__file__)),'xdbtrc.rc')
		if os.path.exists(self.rc):
			fh = open(self.rc,'rb')
			attr = cPickle.load(fh)
			self.attr = dict(self.attr.items() + attr.items())
			fh.close()
	
	def save(self):
		'''Write meta-data to disk.'''
		fh = open(self.rc,'wb')
		cPickle.dump(self.attr,fh)
		fh.close()
		
	def get(self,k):
		'''Retrive attribute'''
		return self.attr[k]
	
	def set(self,k,v):
		'''Define attribute'''
		self.attr[k] = v
	
	def get_geometry(self):
		'''Format attributes to tk geometry string'''
		return '%dx%d+%d+%d' % (self.attr['width'],self.attr['height'],self.attr['root_x'],self.attr['root_y'])
	
	def set_geometry(self,geo):
		'''Parse geometry string to attributes'''
		cords = geo.split('+')
		self.attr['width'], self.attr['height'] = map(int,cords[0].split('x'))
		self.attr['root_x'], self.attr['root_y'] = map(int,cords[1:])
	
	def restore_defaults(self):
		'''Return all attributes to original values'''
		self.attr = self._attr

class Preferences_Dialog(tkSimpleDialog.Dialog):
	'''
		GUI wrapper for Preferences (rc).
		Extends tkSimpleDialog, and should be refactored;
		such that, meta-data attributes can be generated dynamically.
	'''
	attr_message = {
		'background_color' : 'Background Color',
		'base_color'       : 'Base Color',
		'neutral_color'    : 'Neutral Color',
		'primary_color'    : 'Primary Color',
		'secondary_color'  : 'Secondary Color', 
		'tertiary_color'   : 'Tertiary Color',
	}
	def body(self,master):
		'''See tkSimpleDialog.Dialog.body'''
		ri = -1
		for key, message in self.attr_message.items():
			ri += 1
			Label(master,text=message,anchor="w").grid(row=ri)
			_t = Entry(master)
			_t.grid(row=ri,column=1)
			_t.insert(0,self.parent.rc.get(key))
			setattr(self,key,_t)
		ri += 1
		Label(master,text="Restore values", anchor="w").grid(row=ri)
		Button(master,text="Defaults",command=self.restore_defaults).grid(row=ri,column=1)
	
	def restore_defaults(self):
		self.parent.rc.restore_defaults()
		for key in self.attr_message:
			_t = getattr(self,key)
			_t.delete(0,'end')
			_t.insert(0,self.parent.rc.get(key))
		return self.apply()
	
	def apply(self):
		'''See tkSimpleDialog.Dialog.apply'''
		changes = {}
		for a in self.attr_message:
			e = getattr(self,a)
			v = e.get()
			if v != self.parent.rc.get(a):
				self.parent.rc.set(a,v)
				changes[a] = v
		self.result = changes.values()