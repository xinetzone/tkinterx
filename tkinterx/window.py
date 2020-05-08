from tkinter import ttk, filedialog, StringVar

from .graph.canvas_design import Selector
from .graph.drawing import Drawing
from .image_utils import ImageLoader
from .utils import save_bunch, load_bunch, mkdir, FileFrame, FileNotebook


class Graph(Drawing):
    def __init__(self, master=None, cnf={}, **kw):
        super().__init__(master, cnf, **kw)
        self.min_size = (10, 10)
        self.bunch = {}
        self.image_names = ()
        self._image_loader = None
        self._selected_tags = set()

    @property
    def selected_tags(self):
        return self._selected_tags

    @selected_tags.setter
    def selected_tags(self, tags):
        if tags == 'current':
            self._selected_tags = self.find_withtag(tags)
        else:
            self._selected_tags = tags

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
        self.notebook = FileNotebook(
            self.frame, width=200, height=90, padding=(5, 5, 5, 5))
        self.image_frame, self.image_buttons = self.notebook.add_frame(
            [['Load', 'Save'], ['Prev', 'Next']], 'Image')
        self.annotation_frame, self.annotation_buttons = self.notebook.add_frame(
            [['Load', 'Save']], 'Annotation')
        self.init_command()

    def layout(self):
        self.grid(row=0, column=0, sticky='nesw')
        self.xy_status.grid(row=1, column=0, sticky='nesw')
        self.frame.grid(row=2, column=0, sticky='nesw')
        self.selector.layout(row=0, column=0)
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
        self.bunch['root'] = root
        self.draw_image(root)

    def draw_image(self, root):
        self.image_loader = ImageLoader(root)
        self.image_loader.create_image(self, 0, 0, anchor='nw', state='disabled')

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
            self.create_graph(**param)

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
            self.image_loader.create_image(self, 0, 0, anchor='nw')
            self.draw_current_cats()

    def prev_image(self):
        self.delete('image')
        if self.image_loader:
            self.image_loader.current_id -= 1
            self.image_loader.create_image(self, 0, 0, anchor='nw')
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

    def save_graph(self, tags):
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

    def load_graph(self):
        self.bunch = load_bunch('data/annotations.json')
        root = self.bunch['root']
        self.image_loader = ImageLoader(root)
        self.image_names = [
            f"{root}/{image_name}" for image_name in self.bunch if image_name != root]
        self.image_loader.current_id = 0
        self.draw_image(root)
        self.draw_current_cats()


class ScrollableDrawing(Graph):
    def __init__(self, master=None, cnf={}, **kw):
        super().__init__(master, cnf, **kw)
        self._set_scroll()
        self._scroll_command()
        self.configure(xscrollcommand=self.scroll_x.set,
                       yscrollcommand=self.scroll_y.set)
        self.bind("<Configure>", self.resize)
        self.update_idletasks()

    def _set_scroll(self):
        self.scroll_x = ttk.Scrollbar(self, orient='horizontal')
        self.scroll_y = ttk.Scrollbar(self, orient='vertical')

    def _scroll_command(self):
        self.scroll_x['command'] = self.xview
        self.scroll_y['command'] = self.yview

    def resize(self, event):
        region = self.bbox('all')
        self.configure(scrollregion=region)

    def layout(self):
        self.frame.pack(side='top', anchor='w')
        self.selector.layout(row=0, column=0)
        self.notebook.grid(row=0, column=1, sticky='nesw')
        self.scroll_x.pack(side='top', fill='x')
        self.pack(side='top', expand='yes', fill='both')
        self.scroll_y.pack(side='left', fill='y')
        self.xy_status.pack(side='top', fill='y')


class GraphTool(ScrollableDrawing):
    def __init__(self, master=None, cnf={}, **kw):
        super().__init__(master, cnf, **kw)
        self.page_var = StringVar()
        self.jump_stride_var = StringVar()
        self.jump_stride_var.set(1)
        self.create_notebook()
        self.image_loader = None
        self.page_num = 1
        self.master.bind('<Return>', self.update_page)
        self.master.bind('<Control-KeyPress-s>', self.save_rectangle)
        self.bunch = {}
        self._selected_tags = set()

    def show_current_graph(self, *args):
        graph_id = self.find_withtag('current')
        clostest_graph_id = self.find_closest(self.x, self.y, start=2)
        print(self.x, self.y, graph_id, clostest_graph_id)

    def create_notebook(self):
        current_page_label = ttk.Label(self.image_frame, text='current page')
        current_page_entry = ttk.Entry(
            self.image_frame, width='7', textvariable=self.page_var)
        jump_label = ttk.Label(self.image_frame, text='jump stride')
        jump_entry = ttk.Entry(self.image_frame, width='7',
                               textvariable=self.jump_stride_var)
        self.notebook.layout([[jump_label, jump_entry]], start=3)

    def set_image(self):
        self.image_loader.current_id = int(self.page_var.get())
        self.image_loader.create_image(self, 0, 0, anchor='nw')

    def load_images(self, *args):
        root = filedialog.askdirectory()
        if root:
            self.image_loader = ImageLoader(root)
            self.page_num = len(self.image_loader)
            self.page_var.set(0)
            self.set_image()
            self.bunch['root'] = root

    def get_page(self):
        return self.page_var.get(), self.jump_stride_var.get()

    def update_current_page(self, current_page):
        if isinstance(current_page, str):
            current_page = int(current_page)
        if -self.page_num < current_page < self.page_num:
            self.page_var.set(current_page)

    def update_page(self, *args):
        if self.image_loader:
            current_page, jump_stride = self.get_page()
            if '' not in [current_page, jump_stride]:
                self.update_current_page(current_page)
                self.set_image()

    def next_page(self, *args):
        current_page, jump_stride = self.get_page()
        if '' not in [current_page, jump_stride]:
            current_page = int(current_page) + int(jump_stride)
            self.update_current_page(current_page)
            self.set_image()

    def prev_page(self, *args):
        current_page, jump_stride = self.get_page()
        if '' not in [current_page, jump_stride]:
            current_page = int(current_page) - int(jump_stride)
            self.update_current_page(current_page)
            self.set_image()

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

    def save_graph(self, tags):
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

    def save_rectangle(self, *args):
        self.save_graph('rectangle')

    def load_graph(self):
        self.bunch = load_bunch('data/annotations.json')
        root = self.bunch.get()
        if root:
            
            self.image_loader = ImageLoader(root)
            self.image_names = [
                f"{root}/{image_name}" for image_name in self.bunch if image_name != root]
            self.image_loader.current_id = 0
            self.create_image(root)
            self.reload_graph(self.bunch[self.image_loader.current_name])
        else:
            self.bunch = load_bunch('data/normal.json')
            self.load_normal()

    def load_normal(self):
        self.bunch = load_bunch('data/normal.json')
        self.reload_graph(self.bunch)

    def bunch2params(self, bunch):
        params = {}
        for graph_id, cats in bunch.items():
            tags = cats['tags']
            color, shape = tags
            graph_type = shape.split('_')[0]
            bbox = cats['bbox']
            params[graph_id] = {'tags': tags, 'color': color,
                                'graph_type': graph_type, 'direction': bbox}
        return params

    def reload_graph(self, cats):
        params = self.bunch2params(cats)
        self.clear_graph()
        for param in params.values():
            self.draw_graph(**param)

    def clear_graph(self, *args):
        self.delete('all')
        
    def delete_graph(self, *args):
        xy = self.x, self.y
        graph_id = self.find_closest(*xy)
        self.delete(graph_id)

    def select_graph(self, event, tags):
        self.configure(cursor="target")
        self.update_xy(event)
        if tags == 'current':
            self.selected_tags = self.find_withtag(tags)
        else:
            self.selected_tags = tags
        print(self.selected_tags)

    def layout(self):
        self.frame.pack(side='top', anchor='w')
        self.selector.layout(row=0, column=0)
        self.notebook.grid(row=0, column=1, sticky='nesw')
        self.scroll_x.pack(side='top', fill='x')
        self.pack(side='top', expand='yes', fill='both')
        self.scroll_y.pack(side='left', fill='y')
        self.xy_status.pack(side='top', fill='y')

