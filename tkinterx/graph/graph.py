


from tkinter import ttk, StringVar
from tkinterx.param import ParamDict
from tkinterx.graph.canvas import GraphMeta, CanvasMeta
from tkinter import Tk, ttk, Canvas

root = Tk()
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
frame = ttk.Frame(root, width=200, height=200)
self = GraphMeta(root, background='pink')
xy_label = ttk.Label(root, textvariable=self.xy_var)
selector = Selector(frame, background='pink', width=350, height=90)
notebook = ttk.Notebook(frame, width=200, height=100, padding=(5, 5, 5, 5))
annotation = ttk.Frame(notebook, padding=(5, 5, 5, 5))

self.create_circle([50, 50], 20)
frame.grid(row=3, column=0, sticky='nesw')
selector.layout(row=0, column=0)
notebook.grid(row=0, column=1, sticky='nesw')
self.grid(row=0, column=0, sticky='nesw')
xy_label.grid(row=2, column=0, sticky='nesw')

root.mainloop()


class Selector(SelectorMeta):
    '''Binding the left mouse button function of the graphics selector to achieve the color and
        shape of the graphics change.

    Example:
    ===============================================
    from tkinter import Tk
    root = Tk()
    self = SelectorFrame(root, 'rectangle', 'blue')
    self.layout()
    root.mainloop()
    '''
    def __init__(self, master, shape, color, cnf={}, **kw):
        '''The base class of all graphics frames.

        :param master: a widget of tkinter or tkinter.ttk.
        :param graph_type: The initial shape value of the graph.
        :param color: The initial color value of the graph.
        '''
        super().__init__(master, shape, color, cnf, **kw)
        self.bind_selector()

    def bind_selector(self):
        [self.color_bind(self, color)
         for color in SelectorMeta.colors]
        [self.shape_bind(self, shape)
         for shape in SelectorMeta.shapes]

    def update_color(self, new_color):
        self.color = new_color
        self.update_info()

    def update_shape(self, new_shape):
        '''Update graph_type information.'''
        self.shape = new_shape
        self.update_info()

    def color_bind(self, canvas, color):
        canvas.tag_bind(color, '<1>', lambda e: self.update_color(color))

    def shape_bind(self, canvas, shape):
        canvas.tag_bind(shape, '<1>',
                        lambda e: self.update_shape(shape))

    def layout(self, row=0, column=0):
        '''The layout's internal widget.'''
        self.info_frame.grid(row=row, column=column)
        self.info_entry.grid(row=0, column=0, sticky='nwes')
        self.xy_label.grid(row=0, column=1, sticky='nwes')
        self.grid(row=row+1, column=column, sticky='nwes')


class SelectorFrame(ttk.Frame):
    '''Binding the left mouse button function of the graphics selector to achieve the color and
        shape of the graphics change.

    Example:
    ===============================================
    from tkinter import Tk
    root = Tk()
    self = SelectorFrame(root, 'rectangle', 'blue')
    self.layout()
    root.mainloop()
    '''

    def __init__(self, master=None, shape='rectangle', color='blue', **kw):
        '''The base class of all graphics frames.

        :param master: a widget of tkinter or tkinter.ttk.
        :param graph_type: The initial shape value of the graph.
        :param color: The initial color value of the graph.
        '''
        super().__init__(master, **kw)
        self._selector = Selector(
            self, shape, color, background='lightgreen', width=360, height=60)
        self.create_info()
        self._selector.info_var.trace_add('write', self.update_select)

    def create_info(self):
        self.info_var = StringVar()
        self.update_select()
        self.info_entry = ttk.Entry(self, textvariable=self.info_var, width=25)
        self.info_entry['state'] = 'readonly'

    def update_select(self, *args):
        self.info_var.set(self._selector.info_var.get())

    def save_label(self):
        info = f"{self._selector.color} {self._selector.shape}"
        with open('cat.json', 'w') as fp:
            json.dump(info, fp)

    def layout(self, row=0, column=1):
        '''The layout's internal widget.'''
        self.grid(row=row, column=column, sticky='nwes')
        self._selector.grid(row=0, column=0, sticky='we')
        self.info_entry.grid(row=1, column=0, sticky='we')

    def layout_pack(self):
        '''The layout's internal widget.'''
        self._selector.pack(side='left', fill='y')
        self.info_entry.pack(side='left', fill='y')
