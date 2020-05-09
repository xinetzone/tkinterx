from tkinter import Tk
from tkinterx.graph.drawing import Drawing
from tkinterx.graph_utils import ScrollableDrawing
from tkinterx.window import GraphWindow


def test_window():
    root = GraphWindow()
    root.geometry('800x800')
    # root.columnconfigure(0, weight=1)
    # root.rowconfigure(0, weight=1)
    root.layout()
    root.mainloop()


def test1():
    from tkinterx.window import GraphWindow
    root = GraphWindow()
    root.layout()
    root.mainloop()


def test2():
    from tkinterx.window import GraphDrawing
    from tkinter import Tk
    root = Tk()
    root.geometry('800x800')
    self = GraphDrawing(root, width=1000, height=1000, background='darkkhaki')
    self.layout()
    root.mainloop()


if __name__ == "__main__":
    test_window()
