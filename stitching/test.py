from LayoutNode import LayoutNode, ContainerNode, ImageNode, TextNode
from LayoutGenerator import LayoutGenerator, SingleImageLayoutGenerator, GridLayoutGenerator, TextOnImageLayoutGenerator, random_text
# from visualize import visualize_layout
from DataLoader import CustomDataset
import os
import json
import random


# TODO:
# Change LayoutGenerator structure to use image_path
# Increase layout height if grid has many rows
# Generate assymetrical layouts
# Generate layouts with text spanning multiple images

# Test LayoutNode
def test_layout_node():
    node = ContainerNode(0, 0, 100, 100)
    image1 = ImageNode(5, 55, 90, 40, dataset.get_next_image())
    text1 = TextNode(20, 75, 80, 10, "Hello World")
    node.add_child(image1)
    node.add_child(text1)
    image2 = ImageNode(5, 5, 40, 45, dataset.get_next_image())
    image3 = ImageNode(55, 5, 40, 45, dataset.get_next_image())
    text2 = TextNode(20, 10, 80, 20, "Text spanning multiple images in a collage layout with word wrapping")
    collage = ContainerNode(0,0,100,50)
    collage.add_child(image2)
    collage.add_child(image3)
    node.add_child(collage)
    node.add_child(text2)
    os.makedirs("jsons", exist_ok=True)
    with open("jsons/test_layout.json", "w") as f:
        json.dump(node.get_label(), f, indent=2)

    node.save_image("images/test_draw.png")

def sample_layout():
    dataset.get_images(696)
    layout = ContainerNode(0, 0, 800, 600)
    lgen = GridLayoutGenerator(1, 2, spacing=10, with_title=True)
    image_node = lgen.generate(800, 600, 2, 0, dataset.get_images(2))
    text_node = TextNode(100, 200, 200, 300, random_text(2,5))
    layout.add_child(text_node)
    layout.add_child(image_node)
    os.makedirs("jsons", exist_ok=True)
    with open("jsons/sample_layout.json", "w") as f:
        json.dump(layout.get_label(), f, indent=2)
    os.makedirs("images", exist_ok=True)
    layout.save_image("images/sample_layout.png")

# Single Image Layouts
def test_single_image_layouts():
    os.makedirs("jsons", exist_ok=True)
    num_texts = [0,1,1,1,1,2,2,3,3]
    for i in range(len(num_texts)):
        layout_generator = SingleImageLayoutGenerator()
        layout = layout_generator.generate(800, 600, 1, num_texts[i], dataset.get_images(1))

        json.dump(layout.get_label(), open(f"jsons/single_layout_{i+1}.json", "w"), indent=2)
        layout.save_image(f"images/single_layout_{i+1}.png")

# Grid Layouts
def test_grid_layouts():
    os.makedirs("jsons", exist_ok=True)
    os.makedirs("images", exist_ok=True)
    for i in range(1, 4):
        for j in range(1, 4):
            width = 800
            height = 600
            layout_generator = GridLayoutGenerator(i, j)
            num_images = random.randint(max(1, (i * j) // 2), i * j)
            num_texts = i*j - num_images
            layout = layout_generator.generate(width, height, num_images, num_texts, dataset.get_images(num_images))
            json.dump(layout.get_label(), open(f"jsons/grid_layout_{i}x{j}_1.json", "w"), indent=2)
            layout.save_image(f"images/grid_layout_{i}x{j}_1.png")

            space = random.randint(5, 20)
            layout_generator = GridLayoutGenerator(i, j, spacing=space)
            num_images = random.randint(max(1, (i * j) // 2), i * j)
            num_texts = i*j - num_images
            layout = layout_generator.generate(width, height, num_images, num_texts, dataset.get_images(num_images))
            json.dump(layout.get_label(), open(f"jsons/grid_layout_{i}x{j}_2.json", "w"), indent=2)
            layout.save_image(f"images/grid_layout_{i}x{j}_2.png")

            layout_generator = GridLayoutGenerator(i, j, with_title=True)
            num_images = random.randint(max(1, (i * j) // 2), i * j)
            num_texts = i*j - num_images
            layout = layout_generator.generate(width, height, num_images, num_texts, dataset.get_images(num_images))
            json.dump(layout.get_label(), open(f"jsons/grid_layout_{i}x{j}_3.json", "w"), indent=2)
            layout.save_image(f"images/grid_layout_{i}x{j}_3.png")

            space = random.randint(5, 20)
            layout_generator = GridLayoutGenerator(i, j, spacing=space, with_title=True)
            num_images = random.randint(max(1, (i * j) // 2), i * j)
            num_texts = i*j - num_images
            layout = layout_generator.generate(width, height, num_images, num_texts, dataset.get_images(num_images))
            json.dump(layout.get_label(), open(f"jsons/grid_layout_{i}x{j}_4.json", "w"), indent=2)
            layout.save_image(f"images/grid_layout_{i}x{j}_4.png")

    for i in range(1, 6):
        width = 800
        height = 600
        if i > 3:
            height = 800 + (i-3)*300
        layout_generator = GridLayoutGenerator(i, 2, text_only_on_left=True)
        layout = layout_generator.generate(width, height, i, i, dataset.get_images(i))
        json.dump(layout.get_label(), open(f"jsons/order_layout_{i}_1.json", "w"), indent=2)
        layout.save_image(f"images/order_layout_{i}_1.png")

        space = random.randint(5, 20)
        layout_generator = GridLayoutGenerator(i, 2, text_only_on_left=True, spacing=space, with_title=True)
        layout = layout_generator.generate(width, height, i, i, dataset.get_images(i))
        json.dump(layout.get_label(), open(f"jsons/order_layout_{i}_2.json", "w"), indent=2)
        layout.save_image(f"images/order_layout_{i}_2.png")

        layout_generator = GridLayoutGenerator(i, 2, text_only_on_right=True, with_title=True)
        layout = layout_generator.generate(width, height, i, i, dataset.get_images(i))
        json.dump(layout.get_label(), open(f"jsons/order_layout_{i}_3.json", "w"), indent=2)
        layout.save_image(f"images/order_layout_{i}_3.png")

        space = random.randint(5, 20)
        layout_generator = GridLayoutGenerator(i, 2, text_only_on_right=True, spacing=space)
        layout = layout_generator.generate(width, height, i, i, dataset.get_images(i))
        json.dump(layout.get_label(), open(f"jsons/order_layout_{i}_4.json", "w"), indent=2)
        layout.save_image(f"images/order_layout_{i}_4.png")

def test_text_on_image_layouts():
    os.makedirs("jsons", exist_ok=True)
    os.makedirs("images", exist_ok=True)
    for i in range(1, 6):
        for j in range(1, 2 if i>3 else 4):
            width = 800
            height = 600
            if i > 3:
                height = 800 + (i-3)*300
            layout_generator = TextOnImageLayoutGenerator(i, j)
            num_images = i*j
            num_texts = random.randint(0, num_images)
            layout = layout_generator.generate(width, height, num_images, num_texts, dataset.get_images(num_images))
            json.dump(layout.get_label(), open(f"jsons/text_on_image_layout_{i}x{j}_1.json", "w"), indent=2)
            layout.save_image(f"images/text_on_image_layout_{i}x{j}_1.png")

            space = random.randint(5, 20)
            layout_generator = TextOnImageLayoutGenerator(i, j, spacing=space)
            num_images = i*j
            num_texts = random.randint(0, num_images)
            layout = layout_generator.generate(width, height, num_images, num_texts, dataset.get_images(num_images))
            json.dump(layout.get_label(), open(f"jsons/text_on_image_layout_{i}x{j}_2.json", "w"), indent=2)
            layout.save_image(f"images/text_on_image_layout_{i}x{j}_2.png")

            layout_generator = TextOnImageLayoutGenerator(i, j, with_title=True)
            num_images = i*j
            num_texts = random.randint(0, num_images)
            layout = layout_generator.generate(width, height, num_images, num_texts, dataset.get_images(num_images))
            json.dump(layout.get_label(), open(f"jsons/text_on_image_layout_{i}x{j}_3.json", "w"), indent=2)
            layout.save_image(f"images/text_on_image_layout_{i}x{j}_3.png")

            space = random.randint(5, 20)
            layout_generator = TextOnImageLayoutGenerator(i, j, spacing=space, with_title=True)
            num_images = i*j
            num_texts = random.randint(0, num_images)
            layout = layout_generator.generate(width, height, num_images, num_texts, dataset.get_images(num_images))
            json.dump(layout.get_label(), open(f"jsons/text_on_image_layout_{i}x{j}_4.json", "w"), indent=2)
            layout.save_image(f"images/text_on_image_layout_{i}x{j}_4.png")

# visualize
def draw_layouts():
    os.makedirs("images", exist_ok=True)
    for json_file in os.listdir("jsons"):
        if json_file.endswith(".json"):
            visualize_layout(os.path.join("jsons", json_file), f"images/{json_file.replace('.json', '.png')}")
            print(json_file)

dataset = CustomDataset(".")
sample_layout()
test_layout_node()
test_single_image_layouts()
test_grid_layouts()
test_text_on_image_layouts()
# draw_layouts()