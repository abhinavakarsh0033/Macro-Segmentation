from LayoutNode import LayoutNode, ContainerNode, ImageNode, TextNode
from abc import ABC, abstractmethod
import random
import faker

fake = faker.Faker()

# TODO: Check if paths has atleast num_images elements

def random_text(min_words=2, max_words=5) -> str:
    words = fake.words(nb=random.choice([min_words, max_words]))
    return " ".join(words)

class LayoutGenerator(ABC):
    @abstractmethod
    def generate(self, container_width:int, container_height:int, num_images:int, num_texts:int, paths: list) -> LayoutNode:
        pass

class SingleImageLayoutGenerator(LayoutGenerator):
    def generate(self, container_width: int, container_height: int, num_images: int, num_texts: int, paths: list) -> LayoutNode:
        if num_images == 0:
            raise ValueError("No images provided")

        container = ContainerNode(0, 0, container_width, container_height)
        img_cnt = 0

        if num_texts == 0:
            image_node = ImageNode(0, 0, container_width, container_height, paths[img_cnt])
            img_cnt += 1
            container.add_child(image_node)

        else:
            # place the first text beside the image or on the image
            tx, ty, th, tw = 0, 0, 0, 0
            ix, iy, ih, iw = 0, 0, container_height, container_width
            pos = random.choice(['top', 'bottom', 'left', 'right', 'inside'])

            if pos == 'top':
                th = random.randint(container_height // 10, container_height // 2)
                tw = container_width
                tx = 0
                ty = 0
                ix = 0
                iy = th
                ih = container_height - th
                iw = container_width

            elif pos == 'bottom':
                th = random.randint(container_height // 10, container_height // 2)
                tw = container_width
                tx = 0
                ty = container_height - th
                ix = 0
                iy = 0
                ih = container_height - th
                iw = container_width

            elif pos == 'left':
                th = container_height
                tw = random.randint(container_width // 4, container_width // 2)
                tx = 0
                ty = 0
                ix = tw
                iy = 0
                ih = container_height
                iw = container_width - tw

            elif pos == 'right':
                th = container_height
                tw = random.randint(container_width // 4, container_width // 2)
                tx = container_width - tw
                ty = 0
                ix = 0
                iy = 0
                ih = container_height
                iw = container_width - tw

            if pos != 'inside':
                text_node = TextNode(tx, ty, tw, th, random_text())
                container.add_child(text_node)
                num_texts -= 1

            if num_texts > 0:    # atleast one text on the image
                image_container = ContainerNode(ix, iy, iw, ih)
                image_node = ImageNode(ix, iy, iw, ih, paths[img_cnt])
                img_cnt += 1
                image_container.add_child(image_node)
                max_height = image_container.height // num_texts

                for i in range(num_texts):
                    th = random.randint(max_height // 10, min(max_height, image_container.height // 2))
                    tw = random.randint(image_container.width // 4, image_container.width)
                    tx = random.randint(ix, ix + iw - tw)
                    ty = random.randint(iy + i * max_height, iy + (i + 1) * max_height - th)
                    text_node = TextNode(tx, ty, tw, th, random_text())
                    container.add_child(text_node)

            else:
                image_container = ImageNode(ix, iy, iw, ih, paths[img_cnt])
                img_cnt += 1

            container.add_child(image_container)

        return container
    
class GridLayoutGenerator(LayoutGenerator):
    def __init__(self, rows:int, cols:int, spacing:int=0, with_title:bool=False, text_only_on_left:bool=False, text_only_on_right:bool=False):
        self.rows = rows
        self.cols = cols
        self.spacing = spacing
        self.with_title = with_title
        self.text_only_on_left = text_only_on_left
        self.text_only_on_right = text_only_on_right

    def generate(self, container_width: int, container_height: int, num_images: int, num_texts: int, paths: list) -> LayoutNode:
        if num_images == 0:
            raise ValueError("No images provided")

        container = ContainerNode(0, 0, container_width, container_height)
        img_cnt = 0

        # Special cases: override preset rows/cols
        if self.text_only_on_left or self.text_only_on_right:
            self.cols = 2
            self.rows = min(num_images, num_texts)

        th, tw, tx, ty = 0, 0, 0, 0
        if self.with_title:
            th = random.randint(container_height // (3*(self.rows+1)), container_height // (self.rows+1))
            tw = container_width
            tx = 0
            ty = 0
            container.add_child(TextNode(tx, ty, tw, th, random_text()))

        # Create a grid layout
        cell_width = container_width // self.cols
        cell_height = (container_height - th) // self.rows

        for row in range(self.rows):
            for col in range(self.cols):
                x = col * cell_width + self.spacing // 2
                y = row * cell_height + self.spacing // 2 + th
                w = cell_width - self.spacing
                h = cell_height - self.spacing

                if (self.text_only_on_left and col == 0) or (self.text_only_on_right and col == 1):
                    text_node = TextNode(x, y, w, h, random_text())
                    container.add_child(text_node)
                    num_texts -= 1
                    continue

                if (self.text_only_on_left and col == 1) or (self.text_only_on_right and col == 0):
                    image_node = ImageNode(x, y, w, h, paths[img_cnt])
                    container.add_child(image_node)
                    num_images -= 1
                    img_cnt += 1
                    continue

                if num_images > 0 and ((num_texts > 0 and random.choice([True, False])) or num_texts == 0):
                    image_node = ImageNode(x, y, w, h, paths[img_cnt])
                    container.add_child(image_node)
                    num_images -= 1
                    img_cnt += 1
                elif num_texts > 0:
                    text_node = TextNode(x, y, w, h, random_text())
                    container.add_child(text_node)
                    num_texts -= 1

        return container
    
class TextOnImageLayoutGenerator(LayoutGenerator):
    def __init__(self, rows:int, cols:int, spacing:int=0, with_title:bool=False):
        self.rows = rows
        self.cols = cols
        self.spacing = spacing
        self.with_title = with_title

    def generate(self, container_width: int, container_height: int, num_images: int, num_texts: int, paths: list) -> LayoutNode:
        if num_images < self.rows * self.cols:
            raise ValueError("Less images provided")

        container = ContainerNode(0, 0, container_width, container_height)
        img_cnt = 0

        if num_texts > num_images:
            num_texts = num_images

        th, tw, tx, ty = 0, 0, 0, 0
        if self.with_title:
            th = random.randint(container_height // (3*(self.rows+1)), container_height // (self.rows+1))
            tw = container_width
            tx = 0
            ty = 0
            container.add_child(TextNode(tx, ty, tw, th, random_text()))

        # Create a grid layout
        cell_width = container_width // self.cols
        cell_height = (container_height - th) // self.rows

        for row in range(self.rows):
            for col in range(self.cols):
                x = col * cell_width + self.spacing // 2
                y = row * cell_height + self.spacing // 2 + th
                w = cell_width - self.spacing
                h = cell_height - self.spacing

                image_node = ImageNode(x, y, w, h, paths[img_cnt])

                # Place text on image
                if random.choices([True, False], weights=[num_texts, num_images])[0]:
                    txth = random.randint(h // 4, h // 2)
                    txtw = random.randint(w // 3, w)
                    txtx = random.randint(x, x + w - txtw)
                    txty = random.randint(y, y + h - txth)
                    text_node = TextNode(txtx, txty, txtw, txth, random_text())
                    sub_container = ContainerNode(x, y, w, h)
                    sub_container.add_child(image_node)
                    sub_container.add_child(text_node)
                    num_texts -= 1
                else:
                    sub_container = image_node

                container.add_child(sub_container)
                img_cnt += 1
                num_images -= 1

        return container