import os
import cv2
import json
import shutil
import random
from tqdm import tqdm
from utils.yolo_bbox import convert_bbox_to_yolo
from text_recognition.TextRecognizer import TextRecognizer

def process_node(node, img_size):
    bboxes = []
    if node['type'] == 'image':
        bboxes.append(convert_bbox_to_yolo(img_size, node['bbox']))
    
    elif node['type'] == 'container':
        for child in node['children']:
            bboxes.extend(process_node(child, img_size))

    return bboxes


def process_files(name_list, images_path, jsons_path, out_images_path, out_labels_paths):
    recognizer = TextRecognizer()

    for name in tqdm(name_list):
        image_src = os.path.join(images_path, f"{name}.png")
        if not os.path.exists(image_src):
            image_src = os.path.join(images_path, f"{name}.jpg")
        if not os.path.exists(image_src):
            image_src = os.path.join(images_path, f"{name}.jpeg")
        if not os.path.exists(image_src):
            print(f"Image file for {name} not found. Skipping.")
            continue

        img = cv2.imread(image_src)
        if img is None:
            print(f"Failed to load image {image_src}. Skipping.")
            continue
        img_size = (img.shape[1], img.shape[0])  # (width, height)

        image_dest = os.path.join(out_images_path, os.path.basename(image_src))
        # shutil.copy(image_src, image_dest)
        masked_img = recognizer.get_masked_image(image_src)
        cv2.imwrite(image_dest, masked_img)

        with open(os.path.join(jsons_path, f"{name}.json"), 'r') as f:
            node = json.load(f)
        
        label_file = os.path.join(out_labels_paths, f"{name}.txt")
        with open(label_file, 'w') as f:
            bboxes = process_node(node, img_size)
            for bbox in bboxes:
                # 0 is the class id for one image
                f.write(f"0 {bbox[0]} {bbox[1]} {bbox[2]} {bbox[3]}\n")


def create_yolo_dataset(images_path, jsons_path, output_path, split_ratio=0.8):
    """
    Create YOLO formatted dataset from images and corresponding JSON annotations.
    
    Parameters:
    - images_path: Path to the directory containing images.
    - jsons_path: Path to the directory containing JSON annotation files.
    - output_path: Path to the directory where YOLO formatted files will be saved.
    """
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    out_images_path = os.path.join(output_path, 'images')
    out_labels_path = os.path.join(output_path, 'labels')
    out_train_images_path = os.path.join(out_images_path, 'train')
    out_val_images_path = os.path.join(out_images_path, 'val')
    out_train_labels_path = os.path.join(out_labels_path, 'train')
    out_val_labels_path = os.path.join(out_labels_path, 'val')

    os.makedirs(out_train_images_path, exist_ok=True)
    os.makedirs(out_val_images_path, exist_ok=True)
    os.makedirs(out_train_labels_path, exist_ok=True)
    os.makedirs(out_val_labels_path, exist_ok=True)

    extensions = ('.png', '.jpg', '.jpeg')
    name_list = []
    for image_name in os.listdir(images_path):
        name, ext = os.path.splitext(image_name)
        if ext.lower() in extensions:
            json_file = os.path.join(jsons_path, f"{name}.json")
            if not os.path.exists(json_file):
                print(f"JSON file for {image_name} not found. Skipping.")
                continue
            name_list.append(name)
            if len(name_list) >= 10:
                break

    random.shuffle(name_list)
    split_index = int(len(name_list) * split_ratio)
    train_names = name_list[:split_index]
    val_names = name_list[split_index:]
    process_files(train_names, images_path, jsons_path, out_train_images_path, out_train_labels_path)
    process_files(val_names, images_path, jsons_path, out_val_images_path, out_val_labels_path)

    yaml_path = os.path.join(output_path, "macro_seg.yaml")
    with open(yaml_path, "w") as f:
        f.write(f"""train: {os.path.join(output_path, 'images/train')}
val: {os.path.join(output_path, 'images/val')}

nc: 1
names: ['image']
""")


create_yolo_dataset("stitching/images", "stitching/jsons", "./temp")