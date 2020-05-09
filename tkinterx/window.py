from tkinter import Tk

from .graph_utils import ScrollableDrawing
from .meta import ask_window, askokcancel, showwarning
from .meta import PopupLabel


class GraphWindow(Tk):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.on_tune = False
        self.canvas = ScrollableDrawing(
            self, width=600, height=600, background='pink')
        self.bind('<Control-t>', self.bind_graph)
        self.canvas.bind('<Control-e>', self.ask_cat)

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

    def layout(self):
        self.canvas.layout()