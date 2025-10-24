def convert_bbox_to_yolo(img_size, bbox, order=['tl_x', 'tl_y', 'br_x', 'br_y']):
    """
    Convert bounding box to YOLO format (x_center, y_center, width, height).
    
    Parameters:
    - img_size: tuple of (width, height) of the image
    - bbox: tuple or list of bounding box coordinates
    - order: list specifying the order of bbox coordinates
            Current options:
            ['tl_x', 'tl_y', 'br_x', 'br_y'] - top-left x, top-left y, bottom-right x, bottom-right y (Default)
            ['tl_x', 'tl_y', 'width', 'height'] - top-left x, top-left y, width, height
            ['tl', 'tr', 'br', 'bl'] - list of four corner points (top-left, top-right, bottom-right, bottom-left)
    
    Returns:
    - yolo_bbox: tuple in YOLO format
    """
    if order == ['tl_x', 'tl_y', 'br_x', 'br_y']:
        x_center = (bbox[0] + bbox[2]) / 2.0
        y_center = (bbox[1] + bbox[3]) / 2.0
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
    elif order == ['tl_x', 'tl_y', 'width', 'height']:
        x_center = bbox[0] + bbox[2] / 2.0
        y_center = bbox[1] + bbox[3] / 2.0
        width = bbox[2]
        height = bbox[3]
    elif order == ['tl', 'tr', 'br', 'bl']:
        x_center = (bbox[0][0] + bbox[2][0]) / 2.0
        y_center = (bbox[0][1] + bbox[2][1]) / 2.0
        width = bbox[2][0] - bbox[0][0]
        height = bbox[2][1] - bbox[0][1]
    else:
        raise ValueError("Invalid order specified.")

    return (x_center/img_size[0], y_center/img_size[1], width/img_size[0], height/img_size[1])
