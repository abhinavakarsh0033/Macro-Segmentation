from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib import font_manager as fm
import matplotlib.patheffects as patheffects
import textwrap
import cv2

class LayoutNode(ABC):
    def __init__(
        self,
        x: int,
        y: int, 
        width: int,
        height: int
    ) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.depth: int = 0
        self._image_count = 0
        self._text_count = 0

    @property
    @abstractmethod
    def image_count(self) -> int:
        # Currently, it is computed every time but can be cached (seems dangerous)
        pass

    @property
    @abstractmethod
    def text_count(self) -> int:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def update_depth(self, depth: int) -> None:
        pass

    @abstractmethod
    def get_label(self) -> dict:
        pass

    @abstractmethod
    def _draw_node(self, ax) -> None:
        pass

class ContainerNode(LayoutNode):
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int
    ) -> None:
        super().__init__(x, y, width, height)
        self.children: list[LayoutNode] = []
        # self.children = []

    @property
    def image_count(self) -> int:
        return sum(child.image_count for child in self.children)

    @property
    def text_count(self) -> int:
        return sum(child.text_count for child in self.children)

    def update_depth(self, depth: int) -> None:
        # if self.depth == depth:
        #     return
        
        self.depth = depth
        # for child in self.children:
        #     # Increase depth of child if it is a container, else keep the same depth
        #     new_depth = depth + 1 if isinstance(child, ContainerNode) else depth
        #     child.update_depth(new_depth)

        if len(self.children) == 1 and isinstance(self.children[0], ContainerNode):
            # if only one child and it is a container, then keep the same depth
            self.children[0].update_depth(depth)

        else:
            for child in self.children:
                d = depth + 1
                # for image check if some text is on top of it
                if isinstance(child, ImageNode):
                    for other in self.children:
                        if isinstance(other, TextNode):
                            if (other.x < child.x + child.width and
                                other.x + other.width > child.x and
                                other.y < child.y + child.height and
                                other.y + other.height > child.y):
                                # text overlaps with image, increase depth of image
                                d = d + 1
                                break
                child.update_depth(d)

    def _can_fit(self, child: LayoutNode) -> bool:
        return (self.x <= child.x and child.x + child.width <= self.x + self.width and
                self.y <= child.y and child.y + child.height <= self.y + self.height)

    def add_child(self, child: LayoutNode) -> None:
        # check if child can fit in container
        if not self._can_fit(child):
            raise ValueError(f"{child} does not fit in {self}")

        # increase depth of child recursively
        # new_depth = self.depth + 1 if isinstance(child, ContainerNode) else self.depth
        # child.update_depth(new_depth)
        self.children.append(child)
        self.update_depth(self.depth)

    def __str__(self):
        return f"Container (x={self.x}, y={self.y}, {self.width}x{self.height}, depth={self.depth})" + "\n[\n" + "\n".join(str(child) for child in self.children) + "\n]"

    def get_label(self):
        return {
            "type": "container",
            "bbox": (self.x, self.y, self.x+self.width, self.y+self.height),
            "depth": self.depth,
            "children": [child.get_label() for child in self.children]
        }
    
    def _draw_node(self, ax) -> None:
        rect = patches.Rectangle(
            (self.x, self.y),
            self.width,
            self.height,
            facecolor="none"
        )

        if self.depth == 0:
            rect.set_linewidth(2.5)
            rect.set_edgecolor("black")

        ax.add_patch(rect)

        for child in self.children:
            child._draw_node(ax)

    def save_image(self, path:str) -> None:
        fw = 8
        fh = fw * self.height / self.width
        fig, ax = plt.subplots(figsize=(fw, fh))
        ax.set_xlim(self.x, self.x+self.width)
        ax.set_ylim(self.y, self.y+self.height)
        ax.invert_yaxis()
        ax.set_aspect("equal")
        ax.axis("off")

        self._draw_node(ax)
        plt.savefig(path, bbox_inches='tight', pad_inches=0)
        plt.close()
    
class ImageNode(LayoutNode):
    def __init__(self, x:int, y:int, width:int, height:int, image_path:str=""):
        super().__init__(x, y, width, height)
        self.image_path = image_path

    @property
    def image_count(self):
        return 1

    @property
    def text_count(self):
        return 0
    
    def update_depth(self, depth:int):
        self.depth = depth

    def __str__(self):
        return f"Image (x={self.x}, y={self.y}, {self.width}x{self.height}, depth={self.depth})"

    def get_label(self):
        return {
            "type": "image",
            "bbox": (self.x, self.y, self.x+self.width, self.y+self.height),
            "depth": self.depth,
            "image_path": self.image_path
        }
    
    def _draw_node(self, ax) -> None:
        rect = patches.Rectangle(
            (self.x, self.y),
            self.width,
            self.height,
            facecolor="none"
        )
        ax.add_patch(rect)

        img = cv2.imread(self.image_path)
        if img is not None:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # maintain aspect ratio
            img_h, img_w = img.shape[:2]
            if img_w / img_h > self.width / self.height:
                # image is wider than box
                new_h = self.height
                new_w = int(self.height * img_w / img_h)
            else:
                # image is taller than box
                new_w = self.width
                new_h = int(self.width * img_h / img_w)
            im = ax.imshow(img, extent=(self.x, self.x + new_w, self.y + new_h, self.y))
            im.set_clip_path(rect)

        else:
            print(f"Could not read image: {self.image_path}")

        # ax.text(
        #     self.x + self.width / 2,
        #     self.y + self.height / 2,
        #     "IMG" + f" d={self.depth}",
        #     ha = "center",
        #     va = "center",
        #     fontsize = 8,
        #     color = "red"
        # )


""" If you want text on top of multiple images then keep the images in a container 
    and add this container and the text as children to the main container
    +---------+---------+
    |         |         |
    |  +------+------+  |
    |  |    TEXT     |  |
    |  +------+------+  |
    |         |         |
    | Image 1 | Image 2 |
    |         |         |
    +---------+---------+
    The structure should be like:
        Container:
            - Text
            - Container:
                - Image 1
                - Image 2
"""
class TextNode(LayoutNode):
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str = ""
    ) -> None:
        super().__init__(x, y, width, height)
        self.text = text

    @property
    def image_count(self) -> int:
        return 0

    @property
    def text_count(self) -> int:
        return 1

    def update_depth(self, depth: int) -> None:
        self.depth = depth

    def __str__(self):
        return f"Text (x={self.x}, y={self.y}, {self.width}x{self.height}, depth={self.depth})"

    def get_label(self):
        return {
            "type": "text",
            "bbox": (self.x, self.y, self.x+self.width, self.y+self.height),
            "depth": self.depth,
            "text": self.text
        }
    
    def _draw_node(self, ax) -> None:
        rect = patches.Rectangle(
            (self.x, self.y),
            self.width,
            self.height,
            facecolor="none"
        )
        ax.add_patch(rect)

        minfs, maxfs = 4, 24
        fontsize = maxfs

        txt = ax.text(
            self.x + self.width / 2,
            self.y + self.height / 2,
            self.text,
            ha = "center",
            va = "center",
            fontsize = fontsize,
            color = "white",
            fontproperties = fm.FontProperties(fname=fm.findfont("Impact")),
            path_effects=[
                patheffects.Stroke(linewidth=3, foreground="black"),
                patheffects.Normal(),
            ]
        )

        # adjust font size to fit in box
        # TODO: something wrong with width and height (0.75 is temporary fix)
        # print(f"box_width: {width}, box_height: {height}")
        renderer = ax.figure.canvas.get_renderer()
        while fontsize >= minfs:
            txt.set_fontsize(fontsize)
            bbox = txt.get_window_extent(renderer=renderer)
            inv = ax.transData.inverted()
            bbox_data = bbox.transformed(inv)

            text_width = abs(bbox_data.width)
            text_height = abs(bbox_data.height)
            # print(f"text_width: {text_width}, text_height: {text_height}")

            # wrap text if too wide
            if text_width > self.width * 0.9:
                max_chars = max(1, int(len(self.text) * (self.width * 0.9) / text_width))
                wrapped_text = "\n".join(textwrap.wrap(self.text, max_chars))
                txt.set_text(wrapped_text)
                bbox = txt.get_window_extent(renderer=renderer)
                inv = ax.transData.inverted()
                bbox_data = bbox.transformed(inv)
                text_width = abs(bbox_data.width)
                text_height = abs(bbox_data.height)

            if text_width <= self.width * 0.9 and text_height <= self.height * 0.9:
                break
            fontsize -= 1