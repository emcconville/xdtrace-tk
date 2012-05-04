#!/usr/bin/env python
from Tkinter import *
from xdtrace import *

root = Tk()
app = Application(root)
app.mainloop()
try:
  root.destroy()
except TclError :
	print "Nothing to destroy"

exit(0)