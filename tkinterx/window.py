from tkinter import Tk, ttk

from .tools.helper import StatusTool
from .graph_utils import ScrollableDrawing
from .meta import ask_window, askokcancel, showwarning
from .meta import PopupLabel


class Root(Tk):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.statusbar = StatusTool(self, 'bbox: ')
        self.canvas = ScrollableDrawing(self, width=600, height=600, background='pink')
        self.canvas.bind_drawing()
        self.bind('<Motion>', self.upadte_record_bbox)
        self.layout()
        
    def upadte_record_bbox(self, event):
        self.statusbar.var.set(self.canvas.record_bbox)
        
    def layout(self):
        self.canvas.layout()
        self.canvas.pack(side='top', expand='yes', fill='both')
        self.statusbar.pack(side='top', fill='x')


class GraphWindow(Root):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.on_tune = False
        self.bind('<Control-t>', self.bind_graph)
        self.canvas.bind('<3>', self.ask_cat)

    def bind_graph(self, event):
        if self.on_tune:
            self.on_tune = False
            self.canvas.bind_drawing()
        else:
            self.on_tune = True
            self.canvas.bind_selected()

    def ask_cat(self, event):
        bunch = ask_window(self, PopupLabel)
        print(bunch)
        cat_name = bunch['label']
        self.canvas.cat_var.set(cat_name)