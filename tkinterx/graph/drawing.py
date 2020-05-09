from PIL import ImageTk
from tkinter import ttk
from .canvas import GraphDrawing
from ..param import ParamDict


class DrawingMeta(GraphDrawing):
    def __init__(self, master=None, cnf={}, **kw):
        '''
        '''
        super().__init__(master, cnf, **kw)
        self.bind_drawing()
        self.bind_master()

    def bind_master(self):
        self.master.bind('<F1>', self.clear_graph)
        self.master.bind('<Delete>', self.delete_selected)
        self.master.bind('<Control-a>', self.select_all_graph)
        self.master.bind('<Up>', lambda event: self.move_graph(event, 0, -1))
        self.master.bind('<Down>', lambda event: self.move_graph(event, 0, 1))
        self.master.bind('<Left>', lambda event: self.move_graph(event, -1, 0))
        self.master.bind('<Right>', lambda event: self.move_graph(event, 1, 0))
        self.master.bind(
            '<Control-Up>', lambda event: self.scale_graph(event, [0, -1, 0, 0]))
        self.master.bind('<Control-Down>',
                         lambda event: self.scale_graph(event, [0, 1, 0, 0]))
        self.master.bind('<Control-Left>',
                         lambda event: self.scale_graph(event, [-1, 0, 0, 0]))
        self.master.bind('<Control-Right>',
                         lambda event: self.scale_graph(event, [1, 0, 0, 0]))
        self.master.bind('<Control-Shift-Up>',
                         lambda event: self.scale_graph(event, [0, 0, 0, -1]))
        self.master.bind('<Control-Shift-Down>',
                         lambda event: self.scale_graph(event, [0, 0, 0, 1]))
        self.master.bind('<Control-Shift-Left>',
                         lambda event: self.scale_graph(event, [0, 0, -1, 0]))
        self.master.bind('<Control-Shift-Right>',
                         lambda event: self.scale_graph(event, [0, 0, 1, 0]))

    def clear_graph(self, event=None):
        self.delete('graph')

    @property
    def selected_current_graph(self):
        tags = self.gettags('current')
        graph_ids = set(self.find_withtag('current'))
        if 'background' in tags:
            bbox = self.bbox('background')
            graph_ids = set(self.find_enclosed(*bbox)) - graph_ids
        return tuple(graph_ids)

    def delete_selected(self, event):
        self.delete(self.selected_current_graph)

    def select_all_graph(self, event):
        #self.set_select_mode(event)
        self.addtag_withtag('selected', 'graph')

    def scale_graph(self, event, strides):
        bbox = self.bbox('current')
        if bbox:
            x0, y0, x1, y1 = bbox
            x0 += strides[0]+1
            y0 += strides[1]+1
            x1 += strides[2]-1
            y1 += strides[3]-1
            self.coords(self.selected_current_graph, *[x0, y0, x1, y1])

    def move_graph(self, event, x, y):
        self.move(self.selected_current_graph, x, y)

class Drawing(DrawingMeta):
    shape = ParamDict()
    color = ParamDict()
    def __init__(self, master=None, shape='rectangle', color='blue', cnf={}, **kw):
        '''
        '''
        super().__init__(master, cnf, **kw)
        self.shape = shape
        self.color = color
        #self.master.bind('<Control-s>', lambda event: self.save_graph('rectangle', event))

    def finish_drawing(self, event):
        graph_id = self.drawing(self.shape, self.color, width=1, tags=None)
        self.reset()

    def refresh_graph(self, event):
        self.update_xy(event)
        self.after(30, lambda: self.drawing(
            self.shape, self.color, width=2, tags='temp', dash=10))
