from tkinter import ttk, Tk

from .canvas import CanvasMeta
from .canvas_design import SelectorFrame
from ..tools.helper import StatusTool


class GraphMeta(CanvasMeta):
    def __init__(self, master=None, cnf={}, **kw):
        '''
        '''
        super().__init__(master, cnf, **kw)
        '''
        属性
        =====
        record_bbox: [x0, y0, x1, y1]，其中 (x0, y0) 为鼠标单击左键时的 canvas 坐标，当释放鼠标时恢复为 ['none']*2
            (x1, y1) 为鼠标在画布移动时的 canavas 坐标
        '''
        super().__init__(master, **kw)
        self.record_bbox = ['none']*4
        self.statusbar = StatusTool(master, 'bbox: ')
        self.bind_normal()

    def bind_normal(self):
        self.bind('<1>', self.start_record)
        self.bind('<Motion>', self.update_xy)

    def get_canvasxy(self, event):
        '''返回事件的 canvas 坐标'''
        return self.canvasx(event.x), self.canvasy(event.y)

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
        self.grid(row=0, column=0, sticky='nesw')
        self.statusbar.grid(row=1, column=0, sticky='w')


class _GraphCanvas(GraphMeta):
    def __init__(self, master=None, cnf={}, **kw):
        '''
        '''
        super().__init__(master, cnf, **kw)
        self.bind_drawing(master)
        self.bunch = {}  # 记录 canvas 对象

    def bind_drawing(self, master):
        master.bind('<Motion>', self.refresh_graph)
        master.bind('<ButtonRelease-1>', self.finish_drawing)
        master.bind('<F1>', self.clear_graph)
        master.bind('<Delete>', self.delete_graph)
        master.bind('<Up>', lambda event: self.move_graph(event, 0, -1))
        master.bind('<Down>', lambda event: self.move_graph(event, 0, 1))
        master.bind('<Left>', lambda event: self.move_graph(event, -1, 0))
        master.bind('<Right>', lambda event: self.move_graph(event, 1, 0))
        master.bind('<Control-Up>',
                    lambda event: self.scale_graph(event, [0, -1, 0, 0]))
        master.bind('<Control-Down>',
                    lambda event: self.scale_graph(event, [0, 1, 0, 0]))
        master.bind('<Control-Left>',
                    lambda event: self.scale_graph(event, [-1, 0, 0, 0]))
        master.bind('<Control-Right>',
                    lambda event: self.scale_graph(event, [1, 0, 0, 0]))
        master.bind('<Control-Shift-Up>',
                    lambda event: self.scale_graph(event, [0, 0, 0, -1]))
        master.bind('<Control-Shift-Down>',
                    lambda event: self.scale_graph(event, [0, 0, 0, 1]))
        master.bind('<Control-Shift-Left>',
                    lambda event: self.scale_graph(event, [0, 0, -1, 0]))
        master.bind('<Control-Shift-Right>',
                    lambda event: self.scale_graph(event, [0, 0, 1, 0]))

    def mouse_draw_graph(self, graph_type, color='blue', width=1, tags=None, **kw):
        if graph_type == 'point':
            return self.create_square_point(self.record_bbox[2:], color, width, tags, **kw)
        else:
            return self.create_graph(graph_type, self.record_bbox, color, width, tags, **kw)

    def drawing(self, graph_type, color, width=1, tags=None, **kw):
        self.delete('temp')
        if 'none' not in self.record_bbox:
            return self.mouse_draw_graph(graph_type, color, width, tags, activedash=10, **kw)

    def update_tags(self, graph_id):
        return {'tags': self.gettags(graph_id), 'bbox': self.bbox(graph_id)}

    def update_bunch(self, event):
        graph_ids = self.find_withtag('graph')
        params = {graph_id: self.update_tags(graph_id)
                  for graph_id in graph_ids}
        self.bunch = params

    def finish_drawing(self, event, graph_type='rectangle', color='blue', width=1, tags=None, **kw):
        graph_id = self.drawing(
            graph_type, color, width=width, tags=tags, **kw)
        self.bunch.update(self.update_tags(graph_id))
        self.finish_record()

    def refresh_graph(self, event, graph_type='rectangle', color='blue', **kw):
        self.after(30, lambda: self.drawing(graph_type, color, width=2,
                                            tags='temp', dash=10, **kw))

    def clear_graph(self, event):
        self.delete('graph')
        self.bunch = {}

    def delete_graph(self, event):
        graph_id = self.find_withtag('current')
        tags = self.gettags(graph_id)
        if 'graph' in tags:
            self.delete(graph_id)
            self.update_bunch(event)

    @property
    def selected_current_graph(self):
        tags = self.gettags('current')
        graph_ids = set(self.find_withtag('current'))
        if 'background' in tags:
            bbox = self.bbox('background')
            graph_ids = set(self.find_enclosed(*bbox)) - graph_ids
        return tuple(graph_ids)

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
            self.update_bunch(event)

    def move_graph(self, event, x, y):
        self.move(self.selected_current_graph, x, y)
        self.update_bunch(event)


class GraphCanvas(_GraphCanvas):
    def __init__(self, master=None, cnf={}, **kw):
        '''
        '''
        super().__init__(master, cnf, **kw)
        self.min_size = (25, 25)
        self.selector = SelectorFrame(
            master, width=350, height=90, text='Selector', relief='raise')
        self.scroll_x = ttk.Scrollbar(master, orient='horizontal')
        self.scroll_y = ttk.Scrollbar(master, orient='vertical')
        super().__init__(master, **kw)
        self.scroll_x['command'] = self.xview
        self.scroll_y['command'] = self.yview
        self.configure(xscrollcommand=self.scroll_x.set,
                       yscrollcommand=self.scroll_y.set)
        self.update_idletasks()
        self.bind("<Configure>", self.resize)

    def resize(self, event):
        region = self.bbox('all')
        self.configure(scrollregion=region)

    def finish_drawing(self, event, width=1, tags=None, **kw):
        if 'none' not in self.record_bbox:
            x0, y0, x1, y1 = self.record_bbox
            stride_x = abs(x1 - x0)
            stride_y = abs(y1 - y0)
            cond_x = stride_x > self.min_size[0]
            cond_y = stride_y > self.min_size[1]
            if (cond_x and cond_y) or self.selector.shape in ['line', 'point']:
                graph_id = self.drawing(self.selector.shape, self.selector.color,
                                        width=width, tags=tags, **kw)
                self.bunch.update({graph_id: self.update_tags(graph_id)})
                print(self.bunch)
        self.finish_record()

    def refresh_graph(self, event, **kw):
        self.after(30, lambda: self.drawing(self.selector.shape, self.selector.color,
                                            width=2, tags='temp', dash=10, **kw))

    def layout(self):
        self.grid(row=0, column=0, sticky='nesw')
        self.scroll_y.grid(row=0, column=1, sticky='ns')
        self.scroll_x.grid(row=1, column=0, sticky='we')
        self.statusbar.grid(row=2, column=0, sticky='w')
        self.selector.grid(row=3, column=0, sticky='nw')