from tkinter import Tk, Label, ttk
from tkinterx.graph.canvas import CanvasMeta

W, H = 1920, 1080
x, y = [900, 500]
fill = 'red'  # 限速标志的颜色
text = '90'  # 限速标志
spacing = 20 # 正方形边界
r = 420  # 圆环半径
root = Tk()
root.geometry(f'{W}x{H}')
self = CanvasMeta(root, bg='gray')
self.create_text([x, y], text=text, font='楷体 500', fill=fill)
self.create_circle([x, y], r, width=80, color='red')
row = W // spacing
column = H // spacing
for i in range(row):
    for j in range(column):
        self.create_square([i*spacing, j*spacing], spacing, width=2, color='yellowgreen')
self.grid(sticky='nesw')
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.mainloop()