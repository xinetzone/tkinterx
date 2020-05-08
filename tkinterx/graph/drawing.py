from PIL import ImageTk
from tkinter import ttk
from .canvas import GraphDrawing
from .canvas_design import Selector
from ..param import ParamDict


class Drawing(GraphDrawing):
    def __init__(self, master=None, cnf={}, **kw):
        '''
        '''
        super().__init__(master, cnf, **kw)
        self.create_frame()
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

    def create_frame(self):
        self.frame = ttk.Frame(self.master, width=200, height=200)
        self.selector = Selector(
            self.frame, background='pink', width=350, height=90)

    @property
    def shape(self):
        return self.selector.shape

    @property
    def color(self):
        return self.selector.color

    def finish_drawing(self, event):
        graph_id = self.drawing(self.shape, self.color, width=1, tags=None)
        self.reset()

    def refresh_graph(self, event):
        self.update_xy(event)
        self.after(30, lambda: self.drawing(
            self.shape, self.color, width=2, tags='temp', dash=10))

    @property
    def closest_graph_id(self):
        xy = self.record_bbox[2:]
        if xy:
            return self.find_closest(*xy, halo=10)

    def select_current_graph(self, event):
        self.start_record(event)
        if self.selected_current_graph:
            self.configure(cursor="target")
            self.addtag_withtag('selected', self.selected_current_graph)
        else:
            self.configure(cursor="arrow")

    def move_graph(self, event, x, y):
        self.move(self.selected_current_graph, x, y)

    def layout(self):
        self.grid(row=0, column=0, sticky='nesw')
        self.xy_status.grid(row=1, column=0, sticky='nesw')
        self.frame.grid(row=2, column=0, sticky='nesw')
        self.selector.layout(row=0, column=0)


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


class GraphCanvas(Drawing):
    def __init__(self, master=None, cnf={}, **kw):
        '''
        '''
        super().__init__(master, cnf, **kw)
        self.min_size = (10, 10)
        #self.tag_bind('corner_point', '<ButtonRelease-1>', self.tune_corner_point)

    def drawing(self, graph_type, color, width=1, tags=None, **kw):
        self.delete('temp')
        if 'none' not in self.record_bbox:
            x0, y0, x1, y1 = self.record_bbox
            stride_x = x1 - x0
            stride_y = y1 - y0
            cond_x = stride_x > self.min_size[0]
            cond_y = stride_y > self.min_size[1]
            if (cond_x and cond_y) or graph_type in ['line', 'point']:
                return self.mouse_draw_graph(graph_type, color, width, tags, activedash=10, **kw)

    def finish_drawing(self, event):
        graph_id = self.drawing(self.shape, self.color, width=1, tags=None)
        if graph_id:
            record_bbox = self.bbox(graph_id)
            if self.shape not in ['point', 'line']:
                for point in self.get_corner_points(record_bbox):
                    self.create_circle(
                        point, radius=3, fill='yellow', tags=f'corner_point_{graph_id}')
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
        current_id = self.find_withtag('current')
        graph = self.find_below('current')
        if current_id in graph_ids:
            a, b, c, d = self.bbox(current_id)
            center_x = (a + c)/2
            center_y = (b + d)/2
            x0, y0, x1, y1 = self.bbox(graph)
            x = x0 if center_x - x0 < 5 else x1
            y = y0 if center_y - y0 < 5 else y1
            print(x, y)
            #self.coords(graph, )
            self.move('current', *self.strides)
            self.tune_selected(event)

    def finish_corner_point(self, event=None):
        self.move('selected', *self.strides)
        self.delete('corner_point')
        self.cancel_selected(event)

    def select_current_graph(self, event):
        #self.set_select_mode(event)
        self.addtag_withtag('selected', self.closest_graph_id)
