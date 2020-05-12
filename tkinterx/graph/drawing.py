from PIL import ImageTk
from tkinter import ttk
from .canvas import GraphDrawing
from .canvas_design import Selector
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
    def __init__(self, master=None, cnf={}, **kw):
        '''
        '''
        super().__init__(master, cnf, **kw)
        # self.shape = shape
        # self.color = color
        self.create_frame()
    
    def create_frame(self):
        self.frame = ttk.Frame(self.master, width=200, height=200)
        self.selector = Selector(self.frame, background='skyblue', width=350, height=90)

    @property
    def shape(self):
        return self.selector.shape

    @property
    def color(self):
        return self.selector.color

    def finish_drawing(self, event):
        graph_id = self.drawing(self.shape, self.color, width=1, tags=None, activewidth=3)
        self.reset()

    def refresh_graph(self, event):
        self.update_xy(event)
        self.after(30, lambda: self.drawing(
            self.shape, self.color, width=3, tags='temp', dash=10))

    def layout(self, row=0, column=0):
        self.frame.grid(row=row, column=column, sticky='nesw')
        self.selector.grid(row=0, column=0)


class ImageCanvas(Drawing):
    image_path = ParamDict()
    def __init__(self, master, image_path=None, cnf={}, **kw):
        super().__init__(master, cnf, **kw)
        self.image_path = image_path
        if self.image_path:
            self.image = ImageTk.PhotoImage(file=self.image_path)
            self.create_background(0, 0)
        
    def create_background(self, x, y, **kw):
        self.delete('background')
        self.image = ImageTk.PhotoImage(file=self.image_path)
        return self.create_image(x, y, image=self.image, tags='background', **kw)
