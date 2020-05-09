from tkinter import Canvas, StringVar


class CanvasMeta(Canvas):
    '''Graphic elements are composed of line(segment), rectangle, ellipse, and arc.
    '''

    def __init__(self, master=None, cnf={}, **kw):
        '''The base class of all graphics frames.

        :param master: a widget of tkinter or tkinter.ttk.
        '''
        super().__init__(master, cnf, **kw)

    def layout(self, row=0, column=0):
        '''Layout graphic elements with Grid'''
        # Layout canvas space
        self.grid(row=row, column=column, sticky='nwes')

    def create_graph(self, graph_type, direction, color='blue', width=1, tags=None, **kwargs):
        '''Draw basic graphic elements.

        :param direction: Specifies the orientation of the graphic element. 
            Union[int, float] -> (x_0,y_0,x_,y_1), (x_0, y_0) refers to the starting point of 
            the reference brush (i.e., the left mouse button is pressed), and (x_1, y_1) refers to 
            the end position of the reference brush (i.e., release the left mouse button).
            Multipoint sequences are supported for 'line' and 'polygon',
             for example ((x_0, y_0), (x_1, y_1), (x_2, y_2)).
        :param graph_type: Types of graphic elements.
            (str) 'rectangle', 'oval', 'line', 'arc'(That is, segment), 'polygon'.
            Note that 'line' can no longer pass in the parameter 'fill', and 
            the remaining graph_type cannot pass in the parameter 'outline'.
        :param color: The color of the graphic element.
        :param width: The width of the graphic element.(That is, center fill)
        :param tags: The tags of the graphic element. 
            It cannot be a pure number (such as 1 or '1' or '1 2 3'), it can be a list, a tuple, 
            or a string separated by a space(is converted to String tupers separated by a blank space). 
            The collection or dictionary is converted to a string.
            Example:
                ['line', 'graph'], ('test', 'g'), 'line',
                ' line kind '(The blanks at both ends are automatically removed), and so on.
        :param style: Style of the arc in {'arc', 'chord', or 'pieslice'}.

        :return: Unique identifier solely for graphic elements.
        '''
        if tags is None:
            if graph_type in ('rectangle', 'oval', 'line', 'arc'):
                tags = f"graph {color} {graph_type}"
            else:
                tags = f'graph {color}'

        com_kw = {'width': width, 'tags': tags}
        kw = {**com_kw, 'outline': color}
        line_kw = {**com_kw, 'fill': color}
        if graph_type == 'line':
            kwargs.update(line_kw)
        else:
            kwargs.update(kw)
        func = eval(f"self.create_{graph_type}")
        graph_id = func(*direction, **kwargs)
        return graph_id

    def _create_regular_graph(self, graph_type, center, radius, color='blue', width=1, tags=None, **kw):
        '''Used to create a circle or square.
        :param graph_type: 'oval', 'rectangle'
        :param center: (x, y) The center of the regular_graph
        :param radius: Radius of the regular_graph
        '''
        x, y = center
        direction = [x-radius, y - radius, x+radius, y+radius]
        return self.create_graph(graph_type, direction, color, width, tags, **kw)

    def create_circle(self, center, radius, color='blue', width=1, tags=None, **kw):
        '''
        :param center: (x, y) The center of the circle
        :param radius: Radius of the circle
        '''
        return self._create_regular_graph('oval', center, radius, color, width, tags, **kw)

    def create_square(self, center, radius, color='blue', width=1, tags=None, **kw):
        '''
        :param center: (x, y) The center of the square
        :param radius: Radius of the square
        '''
        return self._create_regular_graph('rectangle', center, radius, color, width, tags, **kw)

    def create_circle_point(self, position, color='blue', width=1, tags=None, **kw):
        '''
        :param location: (x, y) The location of the circle_point
        '''
        return self.create_circle(position, 0, color, width, tags, **kw)

    def create_square_point(self, position, color='blue', width=1, tags=None, **kw):
        '''
        :param location: (x, y) The location of the square_point
        '''
        return self.create_square(position, 0, color, width, tags, **kw)


class GraphMeta(CanvasMeta):
    def __init__(self, master=None, cnf={}, **kw):
        '''
        属性
        =====
        record_bbox: [x0, y0, x1, y1]，其中 (x0, y0) 为鼠标单击左键时的 canvas 坐标，当释放鼠标时恢复为 ['none']*2
            (x1, y1) 为鼠标在画布移动时的 canavas 坐标
        '''
        super().__init__(master, cnf, **kw)
        self.record_bbox = ['none']*4

    def bind_normal(self):
        self.bind('<1>', self.start_record)
        self.bind('<Motion>', self.update_xy)
        self.bind('<ButtonRelease-1>', self.finish_record)

    def get_canvasxy(self, event):
        '''返回事件的 canvas 坐标'''
        return self.canvasx(event.x), self.canvasy(event.y)

    def start_record(self, event):
        '''开始记录点击鼠标时的 canvas 坐标'''
        self.record_bbox[:2] = self.get_canvasxy(event)

    def update_xy(self, event):
        '''记录鼠标移动的 canvas 坐标'''
        self.record_bbox[2:] = self.get_canvasxy(event)

    def reset(self):
        self.record_bbox[:2] = ['none']*2

    def finish_record(self, event):
        self.reset()
        self.record_bbox_var.set(self.record_bbox)


class GraphDrawing(GraphMeta):
    def __init__(self, master=None, cnf={}, **kw):
        '''
        '''
        super().__init__(master, cnf, **kw)

    def bind_drawing(self):
        self.bind('<1>', self.start_record)
        self.bind('<Motion>', self.refresh_graph)
        self.bind('<ButtonRelease-1>', self.finish_drawing)

    def mouse_draw_graph(self, graph_type, color='blue', width=1, tags=None, **kw):
        if graph_type == 'point':
            return self.create_square_point(self.record_bbox[2:], color, width, tags, **kw)
        else:
            return self.create_graph(graph_type, self.record_bbox, color, width, tags, **kw)

    def drawing(self, graph_type, color, width=1, tags=None, **kw):
        self.delete('temp')
        if 'none' not in self.record_bbox:
            return self.mouse_draw_graph(graph_type, color, width, tags, activedash=10, **kw)

    def finish_drawing(self, event, graph_type='rectangle', color='blue', width=1, tags=None, **kw):
        self.drawing(graph_type, color, width=1, tags=None, **kw)
        self.reset()

    def refresh_graph(self, event, graph_type='rectangle', color='blue', **kw):
        self.update_xy(event)
        self.after(30, lambda: self.drawing(
            graph_type, color, width=2, tags='temp', dash=10, **kw))
