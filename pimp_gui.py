from pimp_lib import *

from Tkinter import *
from ttk import *
import PIL, Image, ImageTk, random
from tkFileDialog import askopenfilename, asksaveasfilename
from math import log

widgets=[]

class AddWidget:
	def __init__(self, pos):
		pass
		
class Widget:
	def __init__(self, root, column, function=False):
		self.box=Frame(root, relief=SUNKEN, borderwidth=5)
		self.box.grid(row=0, column=column)
		self.add=Button(root, text="Add...")
		self.add.grid(row=1, column=column+1)
		

main=Tk()
main.title("PIMP")
tools_f=Frame(main)
tools_f.grid(row=2, columnspan=100)
widgets.append(Widget(main, 0))
widgets.append(Widget(main, 1))
main.mainloop()
