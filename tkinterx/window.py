from tkinter import Tk, ttk, filedialog, StringVar
from pathlib import Path
from PIL import ImageTk

from .tools.helper import StatusTool
from .graph.drawing import GraphCanvas
from .meta import ask_window, askokcancel, showwarning
from .meta import Table, PopupLabel
from .utils import FileNotebook, mkdir, save_bunch, load_bunch
from .image_utils import ImageLoader


class GraphWindow(Tk):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.bunch = {}
        self.loader = ImageLoader('', 0)
        self.current_image_tk = None
        self.canvas = GraphCanvas(self, bg='pink', highlightthickness=0)
        self.notebook = FileNotebook(self.canvas.selector, width=200,
                                     height=90, padding=2)
        self.create_image_loader()
        self.bind('<Control-l>', self.load_graph)
        self.bind('<Control-s>', self.save_graph)
        self.layout()

    @property
    def current_image_id(self):
        '''获取当前可能存在的背景图'''
        return self.table.todict()['image_id']

    def save_graph(self, event):
        mkdir('data')
        path = 'data/annotations.json'
        if self.current_image_id:
            self.bunch['root'] = self.loader.root.as_posix()
            self.bunch[self.loader.current_name] = self.canvas.bunch
        else:
            self.bunch['default'] = self.canvas.bunch
        save_bunch(self.bunch, path)
        print(self.bunch)

    def load_graph(self, *args):
        try:
            self.bunch = load_bunch('data/annotations.json')
            root = self.bunch.get('root')
            if root:
                self.loader.root = Path(root)
                self.table['image_id'].var.set(0)
                self.create_background()
                self.update_graph(event)
                self.draw_current_cats()
            else:
                self.draw_graph(self.bunch)
        except:
            pass

    def create_image_loader(self):
        self.image_frame = ttk.Frame(self.notebook)
        self.load_image_button = ttk.Button(
            self.image_frame, text='Load', width=5, command=self.load_image)
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

    def create_background(self, x=0, y=0, **kw):
        if self.current_image_id:
            self.canvas.delete('background')
            self.loader.current_id = int(self.current_image_id)
            self.table['image_id'].var.set(self.loader.current_id)
            self.current_image_tk = ImageTk.PhotoImage(
                image=self.loader.current_image)  # 必须与 Tk 同级
            return self.canvas.create_image(x, y, image=self.current_image_tk,
                                            tags='background', anchor='nw', **kw)

    def load_image(self, event=None):
        self.loader.root = Path(filedialog.askdirectory())
        self.table['image_id'].var.set(0)
        if self.loader.names:
            self.bunch['root'] = self.loader.root.as_posix()
            self.create_background()
            self.bunch[self.loader.current_name] = {}

    def change_image(self, event=None):
        if self.loader.names:
            self.save_graph(event)
            self.update_graph(event)
            return True
        else:
            return False

    def bunch2params(self, bunch):
        params = {}
        for graph_id, cats in bunch.items():
            tags = cats['tags']
            _, color, shape, *_ = tags
            graph_type = shape.split('_')[0]
            bbox = cats['bbox']
            params[graph_id] = {'tags': tags, 'color': color,
                                'graph_type': graph_type, 'direction': bbox}
        return params

    def draw_graph(self, cats):
        params = self.bunch2params(cats)
        for param in params.values():
            self.canvas.create_graph(activedash=10, **param)

    def draw_current_cats(self):
        cats = self.bunch.get(self.loader.current_name)
        if cats:
            self.draw_graph(cats)

    def update_graph(self, current_name, canvas_bunch):
        
        if not canvas_bunch:
            self.bunch[current_name] = self.canvas.bunch
        self.create_background()
        self.draw_current_cats()

    def prev_image(self, event=None, **kw):
        last_canvas_bunch = self.bunch[self.loader.current_name]
        self.save_graph(event)
        self.table['image_id'].var.set(int(self.current_image_id)-1)
        canvas_bunch = self.bunch.get(self.loader.current_name)
        self.update_graph(event)
        

    def next_image(self, event=None, **kw):
        self.save_graph(event)
        self.table['image_id'].var.set(int(self.current_image_id)+1)
        self.update_graph(event)

    def layout(self):
        self.canvas.layout()
        self.notebook.grid(row=0, column=1, sticky='nw', padx=5)