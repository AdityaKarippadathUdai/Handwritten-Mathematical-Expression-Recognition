import numpy as np

def preprocess_image(image_bytes: bytes) -> np.ndarray:
    # Decode bytes, resize to YOLO input size (e.g., 640x640), convert to RGB
    # numpy array placeholder
    return np.zeros((640, 640, 3), dtype=np.uint8)
