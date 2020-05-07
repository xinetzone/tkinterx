from tkinter import ttk

from .graph.canvas_design import Selector
from .graph.drawing import Drawing
from .utils import save_bunch, load_bunch, mkdir, FileFrame, FileNotebook


class Graph(Drawing):
    def __init__(self, master=None, cnf={}, **kw):
        super().__init__(master, cnf, **kw)
        self.min_size = (10, 10)

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

    def create_frame(self):
        self.frame = ttk.Frame(self.master, width=200, height=200)
        self.selector = Selector(
            self.frame, background='pink', width=350, height=90)
        self.notebook = ttk.Notebook(
            self.frame, width=200, height=90, padding=(5, 5, 5, 5))
        self.image_frame = ttk.Frame(self.notebook, padding=(5, 5, 5, 5))
        self.next_image_button = ttk.Button(self.image_frame, text='Next')
        self.prev_image_button = ttk.Button(self.image_frame, text='Prev')
        #self.annotation = ttk.Frame(self.notebook, width=200, height=200, padding=(5, 5, 5, 5))
        self.annotation_frame = FileFrame(self.notebook, text='annotations', padding=(5, 5, 5, 5))
        self.notebook.add(self.image_frame, text='Image')
        self.notebook.add(self.annotation_frame, text='Annotation')
        

    def layout(self):
        self.grid(row=0, column=0, sticky='nesw')
        self.xy_status.grid(row=1, column=0, sticky='nesw')
        self.frame.grid(row=2, column=0, sticky='nesw')
        self.selector.layout(row=0, column=0)
        self.notebook.grid(row=0, column=1, sticky='nesw')
        # self.save_normal_button.grid(row=0, column=0, padx=2, pady=2)
        # self.load_normal_button.grid(row=0, column=1, padx=2, pady=2)
        #self.image_frame.grid(row=0, column=0, padx=2, pady=2)
        self.prev_image_button.grid(row=1, column=0, padx=2, pady=2)
        self.next_image_button.grid(row=1, column=1, padx=2, pady=2)
        #self.annotation_frame.grid(row=1, column=0, padx=2, pady=2)
