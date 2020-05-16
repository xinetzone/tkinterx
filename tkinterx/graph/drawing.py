from tkinter import ttk

from .canvas import CanvasMeta
from .canvas_design import SelectorFrame
from ..tools.helper import StatusTool


class CanvasFrame(ttk.Frame):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        '''
        属性
        =====
        record_bbox: [x0, y0, x1, y1]，其中 (x0, y0) 为鼠标单击左键时的 canvas 坐标，当释放鼠标时恢复为 ['none']*2
            (x1, y1) 为鼠标在画布移动时的 canavas 坐标
        '''
        super().__init__(master, **kw)
        self.record_bbox = ['none']*4
        self.statusbar = StatusTool(self, 'bbox: ')
        self.canvas = CanvasMeta(self, width=600, height=600,
                                 bg='pink', highlightthickness=0)
        self.bind_normal(self.canvas)
        self.layout()

    def bind_normal(self, master):
        master.bind('<1>', self.start_record)
        master.bind('<Motion>', self.update_xy)
        #master.bind('<ButtonRelease-1>', self.finish_record)

    def get_canvasxy(self, event):
        '''返回事件的 canvas 坐标'''
        return self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)

    def start_record(self, event):
        '''开始记录点击鼠标时的 canvas 坐标'''
        self.record_bbox[:2] = self.get_canvasxy(event)
        self.statusbar.var.set(self.record_bbox)

    def update_xy(self, event):
        '''记录鼠标移动的 canvas 坐标'''
        self.record_bbox[2:] = self.get_canvasxy(event)
        self.statusbar.var.set(self.record_bbox)

    def reset(self):
        self.record_bbox[:2] = ['none']*2

    def finish_record(self):
        self.reset()
        self.statusbar.var.set(self.record_bbox)

    def layout(self):
        self.canvas.grid(row=0, column=0, sticky='nesw')
        self.statusbar.grid(row=1, column=0, sticky='w')


class DrawingMeta(CanvasFrame):
    def __init__(self, master=None, **kw):
        '''
        '''
        super().__init__(master, **kw)
        self.bind_drawing(master)
        self.bunch = {}  # 记录 canvas 对象

    def bind_drawing(self, master):
        #self.bind('<1>', self.start_record)
        master.bind('<Motion>', self.refresh_graph)
        master.bind('<ButtonRelease-1>', self.finish_drawing)
        master.bind('<F1>', self.clear_graph)
        master.bind('<Delete>', self.delete_graph)

    def mouse_draw_graph(self, graph_type, color='blue', width=1, tags=None, **kw):
        if graph_type == 'point':
            return self.canvas.create_square_point(self.record_bbox[2:], color, width, tags, **kw)
        else:
            return self.canvas.create_graph(graph_type, self.record_bbox, color, width, tags, **kw)

    def drawing(self, graph_type, color, width=1, tags=None, **kw):
        self.canvas.delete('temp')
        if 'none' not in self.record_bbox:
            return self.mouse_draw_graph(graph_type, color, width, tags, activedash=10, **kw)

    def update_bunch(self, graph_id):
        if not graph_id:
            self.bunch[graph_id] = {'tags': self.canvas.gettags(graph_id), 'bbox': self.canvas.bbox(graph_id)}
        else:
            self.bunch.update()

    def finish_drawing(self, event, graph_type='rectangle', color='blue', width=1, tags=None, **kw):
        graph_id = self.drawing(graph_type, color, width=width, tags=tags, **kw)
        self.update_bunch(graph_id)
        self.finish_record()

    def refresh_graph(self, event, graph_type='rectangle', color='blue', **kw):
        self.after(30, lambda: self.drawing(
            graph_type, color, width=2, tags='temp', dash=10, **kw))

    def clear_graph(self, event):
        self.canvas.delete('graph')
        self.bunch.update()
        

    def delete_graph(self, event):
        graph_id = self.canvas.find_withtag('current')
        tags = self.canvas.gettags(graph_id)
        if 'graph' in tags:
            self.canvas.delete('current')
            self.bunch.pop(graph_id)



class Drawing(DrawingMeta):
    def __init__(self, master=None, **kw):
        '''
        '''
        self.selector = SelectorFrame(master, width=350, height=90, text='Selector')
        super().__init__(master, **kw)
        
    def finish_drawing(self, event, width=1, tags=None, **kw):
        graph_id = self.drawing(self.selector.shape, self.selector.color, width=width, tags=tags, **kw)
        if graph_id:
            self.bunch[graph_id] = {'tags': self.canvas.gettags(graph_id), 'bbox': self.canvas.bbox(graph_id)}
        self.finish_record()

    def refresh_graph(self, event, **kw):
        self.after(30, lambda: self.drawing(self.selector.shape, self.selector.color, 
                                            width=2, tags='temp', dash=10, **kw))
        
    def layout(self):
        self.selector.grid(row=0, column=0, sticky='w')
        self.grid(row=1, column=0, sticky='we')
        self.canvas.grid(row=0, column=0, sticky='nesw')
        self.statusbar.grid(row=1, column=0, sticky='w')