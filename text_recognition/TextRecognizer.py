import easyocr
import cv2
from utils.yolo_bbox import convert_bbox_to_yolo

# TODO: Read about image size in yolo format
class TextRecognizer:
    def __init__(self):
        self.reader = easyocr.Reader(['en'])

    def recognize(self, image_path, yolo_format=True):
        results = self.reader.readtext(image_path, paragraph=True)
        if not yolo_format:
            return results
        
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Image at path {image_path} could not be loaded.")
        
        # Return bounding boxes in YOLO format (x_center, y_center, width, height)
        yolo_results = []
        img_size = (img.shape[1], img.shape[0])  # (width, height)
        for bbox, text in results:
            yolo_bbox = convert_bbox_to_yolo(img_size, bbox, ['tl', 'tr', 'br', 'bl'])
            yolo_results.append((yolo_bbox, text))
        return yolo_results

    def get_masked_image(self, image_path):
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Image at path {image_path} could not be loaded.")
        masked_img = img.copy()
        boxes = self.recognize(image_path, False)

        for bbox, _ in boxes:
            (tl, tr, br, bl) = bbox
            x1, y1 = map(int, tl)
            x2, y2 = map(int, br)
            cv2.rectangle(masked_img, (x1, y1), (x2, y2), (255, 255, 255), -1)

        return masked_img

# import os
# recognizer = TextRecognizer()
# images_path = "../stitching/images"
# out_path = "text_results.txt"

# with open(out_path, 'w') as f:
#     for image_name in os.listdir(images_path):
#         if image_name.endswith(('.png', '.jpg', '.jpeg')):
#             image_path = os.path.join(images_path, image_name)
#             texts = recognizer.recognize(image_path)
#             f.write(f"Image: {image_name}\n")
#             for bbox, text in texts:
#                 f.write(f"  Text: {text}, Bounding Box: {bbox}\n")
#             f.write("\n")
#             break

# rec = TextRecognizer()
# img_path = "../stitching/images/310_grid_layout_3x3_1.png"
# res = rec.recognize(img_path, False)
# print(res)
# img = rec.get_masked_image(img_path)
# cv2.imwrite("temp.png", img)