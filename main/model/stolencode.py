# This code comes from the TFLite Object Detection Raspberry Pi sample.
from typing import List, NamedTuple


class Rect(NamedTuple):
    """A rectangle in 2D space."""
    xmin: float
    xmax: float
    ymin: float
    ymax: float


class Category(NamedTuple):
    """A result of a classification task."""
    label: str
    score: float
    index: int


class Detection(NamedTuple):
    """A detected object as the result of an ObjectDetector."""
    bounding_box: Rect
    category: Category
