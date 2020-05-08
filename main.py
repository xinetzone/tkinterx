from tkinter import Tk
from tkinterx.graph.drawing import Drawing
from tkinterx.window import ScrollableDrawing


class GraphWindow(Tk):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.on_tune = False
        self.canvas = ScrollableDrawing(self, width=600, height=600, background='pink')
        self.bind('<Control-t>', self.bind_graph)

    def bind_graph(self, event):
        if self.on_tune:
            self.on_tune = False
            self.canvas.bind_drawing()
        else:
            self.on_tune = True
            self.canvas.bind_selected()

    def layout(self):
        self.canvas.layout()


def test_window():
    root = GraphWindow()
    root.geometry('800x800')
    # root.columnconfigure(0, weight=1)
    # root.rowconfigure(0, weight=1)
    root.layout()
    root.mainloop()


if __name__ == "__main__":
    test_window()
