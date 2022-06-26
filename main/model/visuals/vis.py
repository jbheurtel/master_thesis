import numpy as np
from main.model.visuals.detections import Detection
from typing import List
import cv2

_COLOR_PALETTE = {
    "house": (0, 255, 0),
    "flooded_house": (0, 128, 255),
    "damage": (255, 0, 0),
    "destroyed_house": (64, 64, 64)
}


def visualize(
        image: np.ndarray,
        detections: List[Detection],
        margin=5,
        row_size=15,
        font_size=2,
        font_thickness=2
) -> np.ndarray:
    for detection in detections:
        # Draw bounding_box
        start_point = detection.left, detection.top
        end_point = detection.right, detection.bottom
        # area = '{:0.2e}'.format(detection.area)
        area = detection.area
        item = detection.name
        cv2.rectangle(image, start_point, end_point, _COLOR_PALETTE[item], 3)

        # Draw label and score
        class_name = detection.name
        probability = round(detection.score, 2)
        result_text = class_name + ' (p: ' + str(probability) + ", area: " + str(area) + ')'
        text_location = (margin + detection.right,
                         margin + row_size + detection.top)
        cv2.putText(image, result_text, text_location, cv2.FONT_HERSHEY_PLAIN,
                    font_size, _COLOR_PALETTE[item], font_thickness)

    return image
