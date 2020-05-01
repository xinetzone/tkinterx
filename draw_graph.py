def test1():
    from tkinterx.window import GraphWindow
    root = GraphWindow()
    root.layout()
    root.mainloop()


if __name__ == "__main__":
    from tkinterx.graph.canvas_design import SelectorFrame
    from tkinterx.window import GraphDrawing
    from tkinter import Tk
    root = Tk()
    root.geometry('800x800')
    selector_frame = SelectorFrame(root, 'rectangle', 'blue')
    self = GraphDrawing(root, selector_frame, width=1000,
                        height=1000, background='darkkhaki')
    self.layout()
    root.mainloop()
