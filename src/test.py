import tkinter as tk
from tkinter import ttk

def bDown_Shift(event):
    tv = event.widget
    select = [tv.index(s) for s in tv.selection()]
    select.append(tv.index(tv.identify_row(event.y)))
    select.sort()
    for i in range(select[0],select[-1]+1,1):
        tv.selection_add(tv.get_children()[i])

def bDown(event):
    tv = event.widget
    if tv.identify_row(event.y) not in tv.selection():
        tv.selection_set(tv.identify_row(event.y))    

def bUp(event):
    tv = event.widget
    if tv.identify_row(event.y) in tv.selection():
        tv.selection_set(tv.identify_row(event.y))    

def bUp_Shift(event):
    pass

def bMove(event):
    tv = event.widget
    moveto = tv.index(tv.identify_row(event.y))    
    for s in tv.selection():
        tv.move(s, '', moveto)

root = tk.Tk()

tree = ttk.Treeview(columns=("col1","col2"), 
                    displaycolumns="col2", 
                    selectmode='none')

# insert some items into the tree
for i in range(10):
    tree.insert('', 'end',iid='line%i' % i, text='line:%s' % i, values=('', i))

tree.grid()
tree.bind("<ButtonPress-1>",bDown)
tree.bind("<ButtonRelease-1>",bUp, add='+')
tree.bind("<B1-Motion>",bMove, add='+')
tree.bind("<Shift-ButtonPress-1>",bDown_Shift, add='+')
tree.bind("<Shift-ButtonRelease-1>",bUp_Shift, add='+')

root.mainloop()