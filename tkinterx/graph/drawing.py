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
        #self.bind_drawing()
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

    @property
    def selected_current_graph(self):
        tags = self.gettags('current')
        graph_ids = set(self.find_withtag('current'))
        if 'background' in tags:
            bbox = self.bbox('background')
            graph_ids = set(self.find_enclosed(*bbox)) - graph_ids
        return tuple(graph_ids)

    def clear_graph(self, event=None):
        self.delete('graph')

    def delete_selected(self, event):
        self.delete(self.selected_current_graph)

    def select_all_graph(self, event):
        #self.set_select_mode(event)
        self.addtag_withtag('selected', 'graph')

    def scale_graph(self, event, strides):
        bbox = self.bbox('current')
        width = 1  # 图形的宽度
        if bbox:
            x0, y0, x1, y1 = bbox
            x0 += strides[0] + width
            y0 += strides[1] + width
            x1 += strides[2] - width
            y1 += strides[3] - width
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
        self.selector = Selector(
            self.frame, background='skyblue', width=350, height=90)

    @property
    def shape(self):
        return self.selector.shape

    @property
    def color(self):
        return self.selector.color

    def finish_drawing(self, event):
        graph_id = self.drawing(self.shape, self.color,
                                width=1, tags=None, activewidth=3)
        self.reset()

    def refresh_graph(self, event):
        self.update_xy(event)
        self.after(30, lambda: self.drawing(
            self.shape, self.color, width=3, tags='temp', dash=10))

    def layout(self, row=0, column=0):
        self.frame.grid(row=row, column=column, sticky='nesw')
        self.selector.grid(row=0, column=0)


class ImageCanvas(Drawing):
    def __init__(self, master=None, cnf={}, **kw):
        super().__init__(master, cnf, **kw)   
        self.bunch = {}
        self.min_size = (25, 25)
        self._set_scroll()
        self._scroll_command()
        self.configure(xscrollcommand=self.scroll_x.set,
                       yscrollcommand=self.scroll_y.set)
        self.bind("<Configure>", self.resize)
        self.update_idletasks()

    def _set_scroll(self):
        self.scroll_x = ttk.Scrollbar(self.master, orient='horizontal')
        self.scroll_y = ttk.Scrollbar(self.master, orient='vertical')

    def _scroll_command(self):
        self.scroll_x['command'] = self.xview
        self.scroll_y['command'] = self.yview

    def resize(self, event):
        region = self.bbox('all')
        self.configure(scrollregion=region)

    def clear_graph(self, event=None):
        self.delete('graph')
        self.bunch = {}

    def delete_selected(self, event):
        self.delete(self.selected_current_graph)

    def finish_drawing(self, event, width=1, tags=None, **kw):
        if 'none' not in self.record_bbox:
            x0, y0, x1, y1 = self.record_bbox
            stride_x = abs(x1 - x0)
            stride_y = abs(y1 - y0)
            cond_x = stride_x > self.min_size[0]
            cond_y = stride_y > self.min_size[1]
            if (cond_x and cond_y) or self.shape in ['line', 'point']:
                graph_id = self.drawing(self.shape, self.color, width=width, tags=None, **kw)
                tags = self.gettags(graph_id)
                self.bunch[graph_id] = {'tags': tags, 'bbox': self.bbox(graph_id)}
        self.reset()
