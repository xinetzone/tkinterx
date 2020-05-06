from tkinter import Tk

from tkinterx.graph.canvas import CanvasMeta
from tkinterx.graph.drawing import Drawing

class GraphWindow(Tk):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.on_tune = False
        self.canvas = Drawing(self, background='pink')
        self.bind('<Control-t>', self.bind_graph)

    def bind_graph(self, event):
        if self.on_tune:
            self.on_tune = False
            self.canvas.bind_drawing()
        else:
            self.on_tune = True
            self.canvas.bind_tune()
            
    
    def layout(self):
        self.canvas.layout()

root = GraphWindow()
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.layout()
root.mainloop()