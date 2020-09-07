from PIL import ImageTk
from tkinter import ttk
from .canvas import CanvasMeta
from .canvas_design import Selector
from ..param import ParamDict
from ..vector import Atom, Rectangle


class GraphMeta(CanvasMeta):

    def __init__(self, master, selector, cnf={}, **kw):
        '''
        属性
        =====
        record_bbox: [x0, y0, x1, y1]，其中 (x0, y0) 为鼠标单击左键时的 canvas 坐标，当释放鼠标时恢复为 ['none']*2
            (x1, y1) 为鼠标在画布移动时的 canavas 坐标
        '''
        super().__init__(master, cnf, **kw)
        self.selector = selector
        self.record_bbox = Rectangle(*['none']*2, 'RecordBbox')

    @property
    def shape(self):
        return self.selector.shape

    @property
    def color(self):
        return self.selector.color

    def update_record(self, event):
        '''返回事件的 canvas 坐标'''
        x = self.canvasx(event.x)
        y = self.canvasy(event.y)
        return Atom(x, y, name='Point')

    def start_record(self, event):
        '''开始记录点击鼠标时的 canvas 坐标'''
        self.record_bbox.x = self.update_record(event)

    def update_xy(self, event):
        '''记录鼠标移动的 canvas 坐标'''
        self.record_bbox.y = self.update_record(event)

    def mouse_draw_graph(self, width=0, tags=None, **kw):
        record_bbox = self.record_bbox.bbox()
        kw.update({'color': self.color, 'width': width, 'tags': tags})
        if self.shape == 'point':
            return self.create_point(record_bbox[2:], **kw)
        else:
            return self.create_graph(self.shape, record_bbox, **kw)

    def drawing(self, width=1, tags=None, **kw):
        self.delete('temp')
        if not self.record_bbox.isNull():
            return self.mouse_draw_graph(width, tags, activedash=10, **kw)

    def refresh_graph(self, event, **kw):
        self.update_xy(event)
        self.after(30, lambda: self.drawing(
            width=2, tags='temp', dash=10, **kw))

    def finish_drawing(self, event, width=1, tags=None, **kw):
        self.drawing(width=width, tags=None, **kw)
        self.record_bbox.x = 'none'

    def bind_drawing(self):
        self.bind('<1>', self.start_record)
        self.bind('<Motion>', self.refresh_graph)
        self.bind('<ButtonRelease-1>', self.finish_drawing)


class GraphPainter(GraphMeta):
    def __init__(self, master, selector, cnf={}, **kw):
        super().__init__(master, selector, cnf, **kw)

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

    def clear_graph(self, event=None):
        self.delete('graph')

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


class ImageCanvas(GraphPainter):
    image_path = ParamDict()

    def __init__(self, master, selector, image_path=None, cnf={}, **kw):
        super().__init__(master, selector, cnf, **kw)
        self.image_path = image_path
        if self.image_path:
            self.image = ImageTk.PhotoImage(file=self.image_path)
            self.create_background(0, 0)

    def create_background(self, x, y, **kw):
        self.delete('background')
        self.image = ImageTk.PhotoImage(file=self.image_path)
        return self.create_image(x, y, image=self.image, tags='background', **kw)
