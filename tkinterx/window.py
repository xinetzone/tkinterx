from tkinter import Tk, ttk, filedialog, StringVar
from pathlib import Path
from PIL import ImageTk
from pathlib import Path

from .tools.helper import StatusTool
from .graph.drawing import GraphCanvas
from .meta import ask_window, askokcancel, showwarning
from .meta import Table, PopupLabel
from .utils import FileNotebook, mkdir, save_bunch, load_bunch
from .image_utils import ImageLoader


class ImageCanvas(GraphCanvas):
    def __init__(self, master=None, photo_name=None, cnf={}, **kw):
        '''
        '''
        super().__init__(master, photo_name, cnf, **kw)
        self.loader = ImageLoader('', 0)

    def update_background(self):
        self.photo_name = self.loader.current_path
        self.update_photo(self.image)

    def prev_image(self, *event, **kw):
        if len(self.loader):
            self.loader.current_id -= 1
            self.update_background()

    def next_image(self, *event, **kw):
        if len(self.loader):
            self.loader.current_id += 1
            self.update_background()


class GraphWindow(Tk):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.default_path = 'data/annotations.json'
        self.bunch = {}
        self.copy_current_graph = []
        self.canvas = ImageCanvas(self, bg='pink', highlightthickness=0)
        self.notebook = FileNotebook(self.canvas.selector, width=200,
                                     height=90, padding=2)
        self.create_image_loader()
        self.bind('<Control-l>', self.load_graph)
        self.bind('<Control-s>', self.save_graph)
        self.bind('<Control-c>', self.copy_current_graph)
        self.bind('<Control-v>', self.paste_graph)
        self.layout()

    def create_image_loader(self):
        self.image_frame = ttk.Frame(self.notebook)
        self.load_image_button = ttk.Button(
            self.image_frame, text='New', width=5, command=self.new_create)
        self.table = Table(self.image_frame)
        self.table.add_row('image_id', 'image_id:', width=7)
        self.prev_image_button = ttk.Button(
            self.image_frame, text='Prev', width=5, command=self.prev_image)
        self.next_image_button = ttk.Button(
            self.image_frame, text='Next', width=5, command=self.next_image)
        self.notebook.add(self.image_frame, text='Image')
        self.table['image_id'].entry['validate'] = "focusout"
        self.table['image_id'].entry['validatecommand'] = self.change_image
        self.table.layout(row=0, sticky='w')
        self.load_image_button.grid(row=3, column=0, sticky='w')
        self.prev_image_button.grid(row=3, column=1, sticky='w')
        self.next_image_button.grid(row=3, column=2, sticky='w')

    def new_create(self, *event):
        self.canvas.loader.root = Path(filedialog.askdirectory())
        num = len(self.canvas.loader)
        if num:
            self.canvas.update_background()
            self.table['image_id'].var.set(0)

    def change_image(self, *event):
        current_image_id = self.table['image_id'].var.get()
        num = len(self.canvas.loader)
        if num:
            if current_image_id in [str(k) for k in range(-num, num)]:
                self.canvas.loader.current_id = int(current_image_id)
            self.canvas.update_background()
            self.draw_current_graph()
            return True
        else:
            return False

    def cat2params(self, cat_list):
        params = []
        for cats in cat_list:
            tags = cats['tags']
            _, color, shape, *_ = tags
            graph_type = shape.split('_')[0]
            bbox = cats['bbox']
            params.append({'tags': tags, 'color': color,
                           'graph_type': graph_type, 'direction': bbox})
        return params

    def load_graph(self, *args):
        self.bunch = self.load_bunch()
        if self.bunch.get('root'):
            self.canvas.loader.root = Path(self.bunch['root'])
            num = len(self.canvas.loader)
            if num:
                self.canvas.update_background()
                self.table['image_id'].var.set(0)
                self.draw_current_graph()

    def load_bunch(self):
        path = Path(self.default_path)
        if path.exists():
            bunch = load_bunch(path)
        else:
            bunch = {}
        return bunch

    def save_graph(self, *event):
        mkdir('data')
        self.bunch = self.load_bunch()
        values = self.canvas.bunch.values()
        if values:
            if self.canvas.photo_name:
                current_name = self.canvas.loader.current_name
                root = self.canvas.loader.root.as_posix()
                cats = {current_name: list(values)}
                self.bunch.update({"root":root, **cats})
                save_bunch(self.bunch, self.default_path)

    def _draw_graph(self, cats):
        params = self.cat2params(cats)
        for param in params:
            self.canvas.create_graph(activedash=10, **param)

    def draw_graph(self, name):
        cats = self.bunch.get(name)
        if cats:
            params = self.cat2params(cats)
            for param in params:
                self.canvas.create_graph(activedash=10, **param)

    def draw_current_graph(self):
        name = self.canvas.loader.current_name
        self.draw_graph(name)

    def copy_current_graph(self, event):
        print('1', self.copy_current_graph)
        self.copy_current_graph = list(self.canvas.bunch.copy().values())
        
    def paste_graph(self, event):
        self.draw_graph(self.copy_current_graph)

    def prev_image(self, *event, **kw):
        self.save_graph(event)
        self.canvas.clear_graph(event)
        bunch = self.load_bunch()
        self.canvas.prev_image(event, **kw)
        self.table['image_id'].var.set(self.canvas.loader.current_id)
        self.draw_current_graph()

    def next_image(self, *event, **kw):
        self.save_graph(event)
        self.canvas.clear_graph(event)
        current_cats = self.bunch.get(self.canvas.loader.current_name)
        self.canvas.next_image(event, **kw)
        next_cats = self.bunch.get(self.canvas.loader.current_name)
        if not next_cats:
            if current_cats:
                self._draw_graph(current_cats)
        else:
            self.draw_current_graph()
        self.table['image_id'].var.set(self.canvas.loader.current_id)
        self.bunch.clear()
        
    def layout(self):
        self.canvas.layout()
        self.notebook.grid(row=0, column=1, sticky='nw', padx=5)
