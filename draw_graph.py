def test1():
    from tkinterx.window import GraphWindow
    root = GraphWindow()
    root.layout()
    root.mainloop()


if __name__ == "__main__":
    from tkinterx.window import GraphDrawing
    from tkinter import Tk
    root = Tk()
    root.geometry('800x800')
    self = GraphDrawing(root, width=1000, height=1000, background='darkkhaki')
    self.layout()
    root.mainloop()
