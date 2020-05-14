from tkinter import Tk
from tkinterx.graph.drawing import Drawing
from tkinterx.window import GraphWindow


def test_window():
    root = GraphWindow()
    root.geometry('800x800')
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.layout()
    root.mainloop()


if __name__ == "__main__":
    test_window()