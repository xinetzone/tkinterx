from pathlib import Path
from PIL import Image, ImageTk

from .param import ParamDict


class ImageLoader:
    root = ParamDict()
    current_id = ParamDict()

    def __init__(self, root, current_id=0):
        self.root = Path(root)
        self.current_id = current_id
        self.name_dict = {name: k for k, name in enumerate(self.names)}

    def get_names(self, re_pattern):
        return set([name.parts[-1] for name in self.root.glob(re_pattern)])

    @property
    def names(self):
        png_names = self.get_names('*.png')
        jpg_names = self.get_names('*.jpg')
        bmp_names = self.get_names('*.bmp')
        names = png_names | jpg_names | bmp_names
        return sorted(names)

    def __getitem__(self, index):
        if isinstance(index, slice):
            return [self.root/name for name in self.names[index]]
        else:
            return self.root/self.names[index]

    @property
    def current_name(self):
        return self.names[self.current_id]

    def __len__(self):
        return len(self.names)

    def name2tk(self, name):
        path = self.root / name
        return ImageTk.PhotoImage(file=path)

    @property
    def current_image_tk(self):
        return self.name2tk(self.current_name)

    def create_background(self, x, y, **kw):
        self.delete('background')
        return self.create_image(x, y, image=self.current_image_tk, tags='background', **kw)


# class ImageLoader:
#     root = ParamDict()
#     current_id = ParamDict()
#     def __init__(self, root, current_id=0):
#         self.root = Path(root)
#         self.current_id =  current_id
#         self.name_dict = {name: k for k, name in enumerate(self.names)}

#     def get_names(self, re_pattern):
#         return set([name.parts[-1] for name in self._root.glob(re_pattern)])

#     @property
#     def names(self):
#         png_names = self.get_names('*.png')
#         jpg_names = self.get_names('*.jpg')
#         bmp_names = self.get_names('*.bmp')
#         names = png_names | jpg_names | bmp_names
#         return sorted(names)

#     def __getitem__(self, index):
#         self.current_id = index
#         return self.names[index]

#     def __next__(self):
#         current_id = self.current_id
#         if isinstance(current_id, slice):
#             # 一组图片之后
#             self.current_id = self.name_dict[self[current_id][-1]] + 1
#         else:
#             self.current_id += 1
#         return self[self.current_id]

#     def prev(self):
#         current_id = self.current_id
#         if isinstance(current_id, slice):
#             # 一组图片之前
#             self.current_id = self.name_dict[self[current_id][0]] - 1
#         else:
#             self.current_id -= 1
#         return self[self.current_id]

#     @property
#     def current_path(self):
#         current_id = self.current_id
#         num = len(self)
#         if current_id < -num:
#             self.current_id = -num
#         elif current_id >= num:
#             self.current_id = num-1
#         path = self._root / self.names[self.current_id]
#         return path.as_posix()

#     @property
#     def current_name(self):
#         return self[self.current_id]

#     def path2tk(self, path):
#         return ImageTk.PhotoImage(file=path)

#     @property
#     def current_image_tk(self):
#         return self.path2tk(self.current_path)

#     def update_image(self):
#         path = self.current_path
#         if path:
#             self._current_image = self.current_image_tk
#         else:  # Avoid loading empty picture pictures.
#             self._current_image = None

#     def create_image(self, canvas, x, y, **kw):
#         self.update_image()
#         canvas.create_image(x, y, image=self._current_image, tags='image', **kw)

#     def __len__(self):
#         return len(self.names)
