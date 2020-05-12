from tkinter import ttk, filedialog, StringVar

from .graph.canvas_design import Selector
from .graph.drawing import Drawing
from .image_utils import ImageLoader
from .param import ParamDict
from .meta import Table
from .utils import save_bunch, load_bunch, mkdir, FileFrame, FileNotebook


class ImageCanvas(Drawing):
    def __init__(self, master=None, cnf={}, **kw):
        super().__init__(master, cnf, **kw)
        self.notebook = FileNotebook(
            self.frame, width=200, height=100, padding=(5, 5, 5, 5))
        self.create_image_loader()

    def create_image_loader(self):
        # self.annotation_frame, self.annotation_buttons = self.notebook.add_frame(
        #     [['Load', 'Save']], 'Annotation')
        self.image_frame = ttk.Frame(self.notebook)
        self.table = Table(self.image_frame)
        self.table.add_row('image_dir', 'image_dir:', width=14)
        self.table.add_row('image_id', 'image_id:', width=7)
        self.table.add_row('bbox_id', 'bbox_id:', width=7)
        self.prev_image_button = ttk.Button(
            self.image_frame, text='prev', width=7)
        self.next_image_button = ttk.Button(
            self.image_frame, text='next', width=7)
        self.notebook.add(self.image_frame, text='Image')
        self.table.layout(row=0, sticky='w')
        self.prev_image_button.grid(row=3, column=0, sticky='w')
        self.next_image_button.grid(row=3, column=1, sticky='w')

    def layout(self, row=0, column=0):
        self.frame.grid(row=row, column=column, sticky='nesw')
        self.selector.grid(row=0, column=0)
        self.notebook.grid(row=0, column=1)


class ImageCanvas11(Drawing):
    def __init__(self, master=None, cnf={}, **kw):
        super().__init__(master, cnf, **kw)
        self.notebook = FileNotebook(
            self.frame, width=200, height=100, padding=(5, 5, 5, 5))
        self.create_image_loader()
        self.create_annotation()

    def create_image_loader(self):
        # self.annotation_frame, self.annotation_buttons = self.notebook.add_frame(
        #     [['Load', 'Save']], 'Annotation')
        self.image_frame = ttk.Frame(self.notebook)
        self.table = Table(self.image_frame)
        self.table.add_row('image_dir', 'image_dir: ', width=14)
        self.table.add_row('image_id', 'image_id: ', width=7)
        self.table.add_row('bbox_id', 'bbox_id: ', width=7)
        self.table.layout(row=3)

    def create_annotation(self):
        self.annotation_frame, self.annotation_buttons = self.notebook.add_frame(
            [['Load', 'Save']], 'Annotation')
        self.annotation_buttons[0][0]['command'] = self.load_graph
        self.annotation_buttons[0][1]['command'] = lambda: self.save_graph(
            'rectangle')

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

    def layout(self, row=0, column=0):
        self.frame.grid(row=row, column=column, sticky='nesw')
        self.selector.grid(row=0, column=0)
        self.notebook.grid(row=0, column=1, sticky='nesw')

    def init_command(self):
        self.image_buttons[0][0]['command'] = self.load_images
        self.image_buttons[1][0]['command'] = self.prev_image
        self.image_buttons[1][1]['command'] = self.next_image


class Graph(Drawing):
    def __init__(self, master=None, cnf={}, **kw):
        super().__init__(master, cnf, **kw)
        self.min_size = (10, 10)
        self.bunch = {}
        self.image_names = ()
        self._image_loader = None
        self.create_notebook()
        self.master.bind(
            '<Control-s>', lambda event: self.save_graph('rectangle', event))
        self.master.bind('<Control-l>', self.load_graph)

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

    def create_notebook(self):
        self.notebook = FileNotebook(
            self.frame, width=200, height=100, padding=(5, 5, 5, 5))
        self.image_frame, self.image_buttons = self.notebook.add_frame(
            [['Load', 'Save'], ['Prev', 'Next']], 'Image')
        self.annotation_frame, self.annotation_buttons = self.notebook.add_frame(
            [['Load', 'Save']], 'Annotation')
        self.table = Table(self.image_frame)
        self.table.add_row('image_id', 'image_id: ', width=7)
        self.table.add_row('bbox_id', 'bbox_id: ', width=7)
        self.table.layout(row=3)
        self.init_command()

    def layout(self, row=0, column=0):
        self.frame.grid(row=row, column=column, sticky='nesw')
        self.selector.grid(row=0, column=0)
        self.notebook.grid(row=0, column=1, sticky='nesw')

    def init_command(self):
        self.image_buttons[0][0]['command'] = self.load_images
        self.image_buttons[1][0]['command'] = self.prev_image
        self.image_buttons[1][1]['command'] = self.next_image
        self.annotation_buttons[0][0]['command'] = self.load_graph
        self.annotation_buttons[0][1]['command'] = lambda: self.save_graph(
            'rectangle')

    def load_images(self, *args):
        #self.image_names = filedialog.askopenfilenames(filetypes=[("All files", "*.*"), ("Save files", "*.png")])
        root = filedialog.askdirectory()
        if root:
            self.bunch['root'] = root
            self.draw_image(root)

    def update_background(self, x, y, **kw):
        self.image_loader.update_image()
        self.image_path = self.image_loader.current_path
        self.create_background(x, y, anchor='nw', **kw)

    def draw_image(self, root):
        self.image_loader = ImageLoader(root)
        self.update_background(0, 0)

    def bunch2params(self, bunch):
        params = {}
        for graph_id, cats in bunch.items():
            tags = cats['tags']
            _, color, shape = tags
            graph_type = shape.split('_')[0]
            bbox = cats['bbox']
            params[graph_id] = {'tags': tags, 'color': color,
                                'graph_type': graph_type, 'direction': bbox}
        return params

    def draw_graph(self, cats):
        params = self.bunch2params(cats)
        self.clear_graph()
        for param in params.values():
            self.create_graph(activedash=10, **param)

    @property
    def image_loader(self):
        return self._image_loader

    @image_loader.setter
    def image_loader(self, new):
        self._image_loader = new

    @property
    def current_cats(self):
        return self.bunch.get(self.image_loader.current_name)

    def draw_current_cats(self):
        if self.current_cats:
            self.draw_graph(self.current_cats)

    def next_image(self):
        self.delete('image')
        if self.image_loader:
            self.image_loader.current_id += 1
            self.update_background(0, 0)
            self.draw_current_cats()

    def prev_image(self):
        self.delete('image')
        if self.image_loader:
            self.image_loader.current_id -= 1
            self.update_background(0, 0)
            self.draw_current_cats()

    def get_graph(self, tags):
        cats = {}
        for graph_id in self.find_withtag(tags):
            tags = self.gettags(graph_id)
            bbox = self.bbox(graph_id)
            cats[graph_id] = {'tags': tags, 'bbox': bbox}
        return cats

    def set_path(self, tags):
        if tags == 'all':
            return 'data/normal.json'
        else:
            return 'data/annotations.json'

    def save_graph(self, tags, *args):
        graph = self.get_graph(tags)
        mkdir('data')
        path = self.set_path(tags)
        if self.image_loader:
            current_image_path = self.image_loader.current_path
            if current_image_path:
                self.bunch.update({self.image_loader.current_name: graph})
                save_bunch(self.bunch, path)
        else:
            save_bunch(graph, path)

    def load_graph(self, *args):
        self.bunch = load_bunch('data/annotations.json')
        root = self.bunch.get('root')
        if root:
            self.image_loader = ImageLoader(root)
            self.image_names = [
                f"{root}/{image_name}" for image_name in self.bunch if image_name != root]
            self.image_loader.current_id = 0
            self.draw_image(root)
            self.draw_current_cats()
        else:
            self.draw_graph(self.bunch)


class ScrollableDrawing(Graph):
    def __init__(self, master=None, cnf={}, **kw):
        super().__init__(master, cnf, **kw)
        self._set_scroll()
        self._scroll_command()
        self.configure(xscrollcommand=self.scroll_x.set,
                       yscrollcommand=self.scroll_y.set)
        self.bind("<Configure>", self.resize)
        self.bind('<3>', self.set_label)
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

    def set_label(self, *args):
        if 'graph' in self.gettags('current'):
            graph_id = self.find_withtag('current')
            #self.bunch[graph_id][]
            print(graph_id)

    def layout(self):
        self.frame.pack(side='top', anchor='w')
        self.selector.grid(row=0, column=0)
        self.notebook.grid(row=0, column=1, sticky='nesw')
        self.scroll_x.pack(side='top', fill='x')
        self.scroll_y.pack(side='left', fill='y')
