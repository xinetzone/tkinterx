from .canvas import GraphMeta
from .canvas_design import Selector


class Drawing(GraphMeta):
    '''Set some mouse event bindings to the keyboard.
    '''

    def __init__(self, master=None, cnf={}, **kw):
        '''The base class of all graphics frames.
        :param master: a widget of tkinter or tkinter.ttk.
        '''
        super().__init__(master, cnf, **kw)
        self.selector = Selector(master, 'rectangle', 'blue')
        self.bind('<Motion>', self.refresh_graph)
        self.bind('<ButtonRelease-1>', self.finish_drawing)

    def mouse_draw_graph(self, graph_type, color='blue', width=1, tags=None, **kw):
        if graph_type == 'point':
            return self.create_square_point(self.record_bbox[2:], color, width, tags, **kw)
        else:
            return self.create_graph(graph_type, self.record_bbox, color, width, tags, **kw)

    @property
    def color(self):
        return self.selector.color

    @property
    def shape(self):
        return self.selector.shape

    def drawing(self, tags=None, width=1, **kw):
        self.delete('temp')
        if 'none' not in self.record_bbox:
            return self.mouse_draw_graph(self.shape, self.color, width, tags, activedash=10, **kw)

    def finish_drawing(self, event):
        self.tag_bind('drawing', '<ButtonRelease-1>', self.finish_drawing)
        self.drawing()
        self.reset()

    def refresh_graph(self, event, **kw):
        self.update_xy(event)
        self.after(30, lambda: self.drawing(
            width=2, tags='temp', dash=10, **kw))
