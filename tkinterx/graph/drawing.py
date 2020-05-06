from tkinter import ttk
from .canvas import GraphMeta
from .canvas_design import Selector


class GraphCanvas(GraphMeta):
    def __init__(self, master=None, cnf={}, **kw):
        '''
        '''
        super().__init__(master, cnf, **kw)
        self.create_frame()
        self.bind_drawing()
        self.bind_master()

    def bind_master(self):
        self.master.bind('<F1>', self.clear_all)
        self.master.bind('<Delete>', self.delete_selected)
        self.master.bind('<Control-a>', self.select_all_graph)
        self.master.bind('<Up>', lambda event: self.move_graph(event, 0, -1))
        self.master.bind('<Down>', lambda event: self.move_graph(event, 0, 1))
        self.master.bind('<Left>', lambda event: self.move_graph(event, -1, 0))
        self.master.bind('<Right>', lambda event: self.move_graph(event, 1, 0))

    def clear_all(self, event):
        self.delete('all')

    def delete_selected(self, event):
        self.delete('current')

    def select_all_graph(self, event):
        self.set_select_mode(event)
        self.addtag_withtag('selected', 'all')

    def create_frame(self):
        self.frame = ttk.Frame(self.master, width=200, height=200)
        self.selector = Selector(
            self.frame, background='pink', width=350, height=90)
        self.notebook = ttk.Notebook(
            self.frame, width=200, height=90, padding=(5, 5, 5, 5))
        self.annotation = ttk.Frame(self.notebook, padding=(5, 5, 5, 5))

    @property
    def shape(self):
        return self.selector.shape

    @property
    def color(self):
        return self.selector.color

    def finish_drawing(self, event):
        self.drawing(self.shape, self.color, width=1, tags=None)
        self.reset()

    def refresh_graph(self, event):
        self.update_xy(event)
        self.after(30, lambda: self.drawing(
            self.shape, self.color, width=2, tags='temp', dash=10))

    @property
    def closest_graph_id(self):
        xy = self.record_bbox[2:]
        if xy:
            return self.find_closest(*xy)

    def move_graph(self, event, x, y):
        graph_id = self.closest_graph_id
        self.move(graph_id, x, y)

    def layout(self):
        self.grid(row=0, column=0, sticky='nesw')
        self.xy_label.grid(row=1, column=0, sticky='nesw')
        self.frame.grid(row=2, column=0, sticky='nesw')
        self.selector.layout(row=0, column=0)
        self.notebook.grid(row=0, column=1, sticky='nesw')


class Drawing(GraphCanvas):
    def __init__(self, master=None, cnf={}, **kw):
        '''
        '''
        super().__init__(master, cnf, **kw)
        self.min_size = (10, 10)
        self.tag_bind('graph', '<Enter>', self.set_outline)
        #self.tag_bind('corner_point', '<ButtonRelease-1>', self.tune_corner_point)

    def set_outline(self, event):
        self.itemconfigure('graph', activedash=10)

    def drawing(self, graph_type, color, width=1, tags=None, **kw):
        self.delete('temp')
        if 'none' not in self.record_bbox:
            x0, y0, x1, y1 = self.record_bbox
            stride_x = x1 - x0
            stride_y = y1 - y0
            cond_x = stride_x > self.min_size[0]
            cond_y = stride_y > self.min_size[1]
            if cond_x and cond_y:
                return self.mouse_draw_graph(graph_type, color, width, tags, activedash=10, **kw)

    def finish_drawing(self, event):
        graph_id = self.drawing(self.shape, self.color, width=1, tags=None)
        if graph_id:
            record_bbox = self.bbox(graph_id)
            for point in self.get_corner_points(record_bbox):
                self.create_circle(
                    point, radius=5, fill='yellow', tags=f'corner_point_{graph_id}')
        self.reset()

    def get_corner_points(self, record_bbox):
        if 'none' not in record_bbox:
            x0, y0, x1, y1 = record_bbox
            return [x0, y0], [x1, y0], [x1, y1], [x0, y1]

    def delete_corner_points(self, event):
        self.after(100, lambda: self.delete('corner_point'))
        
    def tune_selected(self, event=None):
        strides = self.strides
        self.move('selected', *strides)
        graph_id = self.find_withtag('selected')
        self.move('corner_point', *strides)
        self.cancel_selected(event)

    def tune_corner_point(self, event):
        graph_ids = self.find_withtag('corner_point')
        if self.find_withtag('current') in graph_ids:
            self.move('current', *self.strides)
            self.tune_selected(event)

    def finish_corner_point(self, event=None):
        self.move('selected', *self.strides)
        self.delete('corner_point')
        self.cancel_selected(event)

