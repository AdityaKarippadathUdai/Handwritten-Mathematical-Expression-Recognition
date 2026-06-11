import cv2
import numpy as np
from app.services.image_preprocessing import ImagePreprocessingService

def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    Decodes the image bytes, runs it through the ImagePreprocessingService pipeline,
    and returns a 3-channel preprocessed image of shape (640, 640, 3) with uint8 format
    to maintain compatibility with standard YOLO and backend service expectations.
    """
    service = ImagePreprocessingService(target_size=(640, 640))
    
    # 1. Load image
    img = service.load_image(image_bytes)
    
    # 2. Grayscale conversion
    gray = service.convert_to_grayscale(img)
    
    # 3. Noise removal
    denoised = service.remove_noise(gray, method="gaussian", kernel_size=5)
    
    # 4. Contrast enhancement
    enhanced = service.enhance_contrast(denoised, clip_limit=2.0)
    
    # 5. Adaptive thresholding
    binary = service.adaptive_threshold(enhanced, block_size=11, constant_c=2, invert=True)
    
    # 6. Resize with padding
    resized = service.resize_with_padding(binary, target_size=(640, 640), fill_value=0)
    
    # Convert single channel grayscale back to 3-channel BGR to match signature
    three_channel = cv2.cvtColor(resized, cv2.COLOR_GRAY2BGR)
    return three_channel

