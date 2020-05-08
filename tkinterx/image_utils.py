from pathlib import Path
from PIL import Image, ImageTk


class ImageLoader:
    def __init__(self, root):
        self._root = Path(root)
        self._init_params()
        self.name_dict = {name: k for k, name in enumerate(self.names)}

    def _init_params(self):
        self.current_id = 0
        self._current_image = None

    @property
    def root(self):
        return self._root.as_posix()

    @root.setter
    def root(self, new_root):
        self._root = Path(new_root)

    def get_names(self, re_pattern):
        return set([name.parts[-1] for name in self._root.glob(re_pattern)])

    @property
    def names(self):
        png_names = self.get_names('*.png')
        jpg_names = self.get_names('*.jpg')
        names = png_names | jpg_names
        return sorted(names)

    def __getitem__(self, index):
        self.current_id = index
        return self.names[index]

    def __next__(self):
        current_id = self.current_id
        if isinstance(current_id, slice):
            # 一组图片之后
            self.current_id = self.name_dict[self[current_id][-1]] + 1
        else:
            self.current_id += 1
        return self[self.current_id]

    def prev(self):
        current_id = self.current_id
        if isinstance(current_id, slice):
            # 一组图片之前
            self.current_id = self.name_dict[self[current_id][0]] - 1
        else:
            self.current_id -= 1
        return self[self.current_id]

    @property
    def current_path(self):
        current_id = self.current_id
        num = len(self)
        if current_id < -num:
            self.current_id = -num
        elif current_id >= num:
            self.current_id = num-1
        path = self._root / self.names[self.current_id]
        return path.as_posix()

    @property
    def current_name(self):
        return self[self.current_id]

    def path2tk(self, path):
        return ImageTk.PhotoImage(file=path)

    @property
    def current_image_tk(self):
        return self.path2tk(self.current_path)

    def update_image(self):
        path = self.current_path
        if path:
            self._current_image = self.current_image_tk
        else:  # Avoid loading empty picture pictures.
            self._current_image = None

    def create_image(self, canvas, x, y, **kw):
        self.update_image()
        canvas.create_image(x, y, image=self._current_image, tags='image', **kw)

    def __len__(self):
        return len(self.names)
