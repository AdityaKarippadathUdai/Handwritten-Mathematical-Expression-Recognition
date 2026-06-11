import os
import threading
from typing import List, Dict, Any, Union
import numpy as np
import cv2
import torch
from ultralytics import YOLO

from app.core.config import settings


class SymbolDetectionService:
    """
    Singleton service for YOLOv11 Handwritten Mathematical Symbol Detection.
    
    This service loads the YOLOv11 model weights once at startup, utilizes GPU/CUDA
    acceleration if available, falls back to CPU if CUDA is not available or if load fails,
    and implements a thread-safe Singleton pattern.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        # Thread-safe Double-Checked Locking singleton implementation
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(SymbolDetectionService, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_path: str = None) -> None:
        """
        Initializes the YOLOv11 symbol detection model.
        Loads the model weights and sets up the execution device.
        """
        if getattr(self, "_initialized", False):
            return

        self.model_path = model_path or settings.YOLO_MODEL_PATH
        
        # Check GPU availability and configure fallback
        if torch.cuda.is_available():
            self.device = "cuda"
        else:
            self.device = "cpu"
            
        print(f"Initializing YOLOv11 symbol detection service. Device: {self.device}")
        
        # Load Ultralytics YOLO model once
        try:
            if not os.path.exists(self.model_path):
                print(f"WARNING: Model file not found at: {self.model_path}")
            
            self.model = YOLO(self.model_path)
            
            # Transfer model to GPU if CUDA was selected
            if self.device == "cuda":
                try:
                    self.model.to(self.device)
                except Exception as e:
                    print(f"Failed to load YOLO model on GPU: {e}. Falling back to CPU.")
                    self.device = "cpu"
                    self.model.to(self.device)
        except Exception as e:
            print(f"Critical error loading YOLO model: {e}. Running in uninitialized state.")
            self.model = None

        self._initialized = True

    def detect(self, image: np.ndarray, confidence_threshold: float = 0.25) -> List[Dict[str, Any]]:
        """
        Performs inference on a preprocessed image to detect mathematical symbols.

        Args:
            image: Preprocessed image. Can be a grayscale array (H, W), a single-channel array
                   (H, W, 1), or a multi-channel standard array (H, W, 3).
            confidence_threshold: Minimum confidence score to keep a detection.

        Returns:
            List[Dict[str, Any]]: List of dictionaries containing the detected symbol name,
                                  confidence score, and bounding box coordinates:
                                  [
                                    {
                                      "symbol": "(",
                                      "confidence": 0.98,
                                      "bbox": [x1, y1, x2, y2]
                                    }
                                  ]
        """
        if self.model is None:
            raise RuntimeError(
                f"YOLO model is not loaded. Check model weights path: {self.model_path}"
            )

        # Standardize the input image to 3-channel BGR format expected by YOLO
        input_img = image
        if len(input_img.shape) == 2:
            input_img = cv2.cvtColor(input_img, cv2.COLOR_GRAY2BGR)
        elif len(input_img.shape) == 3 and input_img.shape[2] == 1:
            input_img = cv2.cvtColor(input_img, cv2.COLOR_GRAY2BGR)

        # Ensure image is in uint8 format (YOLO expectations)
        if input_img.dtype != np.uint8:
            # If normalized float array [0.0, 1.0], scale to [0, 255]
            if input_img.max() <= 1.0:
                input_img = (input_img * 255.0).astype(np.uint8)
            else:
                input_img = input_img.astype(np.uint8)

        # Run model inference
        # conf=confidence_threshold filters detections during inference
        results = self.model(input_img, device=self.device, conf=confidence_threshold, verbose=False)
        
        detections = []
        if len(results) > 0:
            result = results[0]
            if result.boxes is not None:
                for box in result.boxes:
                    # xyxy coordinates: [x1, y1, x2, y2]
                    xyxy = box.xyxy[0].tolist()
                    conf = float(box.conf[0])
                    cls_id = int(box.cls[0])
                    
                    # Look up class name from model names metadata dynamically
                    symbol_name = self.model.names.get(cls_id, f"class_{cls_id}")
                    
                    detections.append({
                        "symbol": symbol_name,
                        "confidence": conf,
                        "bbox": xyxy
                    })
                    
        return detections
