
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
	}
	def __init__(self):
		'''Generate rc filename, and load existing rc if found.'''
		self.rc = os.path.join(os.path.dirname(os.path.abspath(__file__)),__file__+'.rc')
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

class Preferences_Dialog(tkSimpleDialog.Dialog):
	'''
		GUI wrapper for Preferences (rc).
		Extends tkSimpleDialog, and should be refactored;
		such that, meta-data attributes can be generated dynamically.
	'''
	def body(self,master):
		'''See tkSimpleDialog.Dialog.body'''
		Label(master,text="Graph line color").grid(row=0)
		Label(master,text="Graph selected color").grid(row=1)
		Label(master,text="Graph function color").grid(row=2)
		self.base_color = Entry(master)
		self.primary_color = Entry(master)
		self.secondary_color = Entry(master)
		self.base_color.grid(row=0,column=1)
		self.primary_color.grid(row=1,column=1)
		self.secondary_color.grid(row=2,column=1)
		self.base_color.insert(0,self.parent.rc.get('base_color'))
		self.primary_color.insert(0,self.parent.rc.get('primary_color'))
		self.secondary_color.insert(0,self.parent.rc.get('secondary_color'))
	def apply(self):
		'''See tkSimpleDialog.Dialog.apply'''
		changes = {}
		for a in ['base_color','primary_color','secondary_color']:
			e = getattr(self,a)
			v = e.get()
			if v != self.parent.rc.get(a):
				self.parent.rc.set(a,v)
				changes[a] = v
		self.result = changes.values()