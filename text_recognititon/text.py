import easyocr
import os

def recognize_text(images_path):
    reader = easyocr.Reader(['en'])
    results = []
    for image_name in os.listdir(images_path):
        if image_name.endswith(('.png')):
            image_path = os.path.join(images_path, image_name)
            result = reader.readtext(image_path, paragraph=True)
            results.append((image_name, result))
            if(len(results) >= 20):
                break
    return results


results = recognize_text("../stitching/images")
out_path = "text_results.txt"
with open(out_path, 'w') as f:
    for image_name, texts in results:
        f.write(f"Image: {image_name}\n")
        # for bbox, text, conf in texts:
            # f.write(f"  Text: {text}, Confidence: {conf}, Bounding Box: {bbox}\n")
        # f.write(texts.__str__())
        for bbox, text in texts:
            f.write(f"  Text: {text}, Bounding Box: {bbox}\n")
        f.write("\n")