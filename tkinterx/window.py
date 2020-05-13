from tkinter import Tk, ttk, filedialog
from pathlib import Path
from PIL import ImageTk

from .tools.helper import StatusTool
from .graph.drawing import ImageCanvas
from .meta import ask_window, askokcancel, showwarning
from .meta import PopupLabel, Table
from .utils import FileNotebook
from .image_utils import ImageLoader


class Root(Tk):
    def __init__(self):
        super().__init__()
        self.statusbar = StatusTool(self, 'bbox: ')
        self.loader = ImageLoader('', 0)
        self.current_image_tk = None
        self.canvas = ImageCanvas(self, bg='pink', width=600, height=600)
        self.notebook = FileNotebook(
            self.canvas.frame, width=200, height=100, padding=(2, 2, 2, 2))
        self.create_image_loader()
        self.bind('<Motion>', self.upadte_record_bbox)
        self.layout()

    def upadte_record_bbox(self, event):
        self.statusbar.var.set(self.canvas.record_bbox)

    def create_image_loader(self):
        self.image_frame = ttk.Frame(self.notebook)
        self.load_image_button = ttk.Button(
            self.image_frame, text='Load', width=5, command=self.load_image)
        self.table = Table(self.image_frame)
        self.table.add_row('image_id', 'image_id:', width=7)
        self.table.add_row('bbox_id', 'bbox_id:', width=7)
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
            return self.canvas.create_image(x, y, image=self.current_image_tk, tags='background', **kw)

    def load_image(self, event=None):
        self.loader.root = Path(filedialog.askdirectory())
        self.table['image_id'].var.set(0)
        self.create_background()

    def change_image(self, *args):
        if self.loader.names:
            self.create_background()
            return True
        else:
            return False

    @property
    def current_image_id(self):
        return self.table.todict()['image_id']

    def prev_image(self, *args, **kw):
        if self.current_image_id and self.loader.names:
            self.table['image_id'].var.set(int(self.current_image_id)-1)
        self.create_background()

    def next_image(self, *args, **kw):
        if self.current_image_id and self.loader.names:
            self.table['image_id'].var.set(int(self.current_image_id)+1)
        self.create_background()

    def layout(self):
        self.canvas.grid(row=0, column=0, sticky='nesw')
        self.canvas.scroll_x.grid(row=1, column=0, sticky='we')
        self.canvas.scroll_y.grid(row=0, column=1, sticky='ns')
        self.canvas.frame.grid(row=2, column=0, sticky='nw') 
        self.canvas.selector.grid(row=0, column=0, sticky='nw')
        self.notebook.grid(row=0, column=1, sticky='nw')
        self.statusbar.grid(row=3, column=0, sticky='nw') 


class GraphWindow(Root):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.canvas.bind_drawing()
        