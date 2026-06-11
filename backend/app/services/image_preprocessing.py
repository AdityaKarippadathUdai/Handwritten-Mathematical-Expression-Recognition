import cv2
import numpy as np
from pathlib import Path
from typing import Union, Tuple, Dict, Any


class ImagePreprocessingService:
    """
    Service for preprocessing handwritten mathematical expression images.
    
    This service prepares raw, user-uploaded images for downstream machine learning/deep learning
    inference (e.g., character segmentation, YOLO symbol detection, or sequence recognition).
    
    It implements the following sequential steps:
    1. Image Loading and Decoding
    2. Grayscale Conversion (reducing color channel complexity)
    3. Noise Removal (smoothing out scan lines, paper textures, or camera noise)
    4. Contrast Enhancement (using CLAHE to bring out faint handwriting strokes)
    5. Adaptive Thresholding (handling uneven lighting/shadows to isolate ink strokes)
    6. Aspect-Ratio Preserving Resizing with Padding (preventing symbol shape distortion)
    7. Normalization (scaling intensity values to float range [0.0, 1.0] for stable model convergence)
    """

    def __init__(self, target_size: Tuple[int, int] = (640, 640)) -> None:
        """
        Initializes the preprocessing service.

        Args:
            target_size: The target (height, width) dimensions expected by the model.
                         Defaults to (640, 640), which is the standard size for YOLO inputs.
        """
        self.target_size = target_size

    def load_image(self, image_source: Union[bytes, np.ndarray, str, Path]) -> np.ndarray:
        """
        Loads and decodes the image from various source formats into a standard BGR NumPy array.

        Explanation:
            Input images can come as raw file bytes (uploaded via FastAPI/REST), file paths,
            or already-loaded NumPy arrays. This helper method standardizes the input source
            so the downstream pipeline receives a consistent 3-channel BGR numpy array.

        Args:
            image_source: Image input as raw bytes, a file path (str/Path), or a NumPy array.

        Returns:
            np.ndarray: BGR image array.

        Raises:
            ValueError: If the image source format is invalid or cannot be decoded.
        """
        if isinstance(image_source, np.ndarray):
            # Already a numpy array; return a copy or verify dimensions
            if len(image_source.shape) < 2:
                raise ValueError("Input NumPy array has invalid dimensions.")
            return image_source.copy()

        elif isinstance(image_source, bytes):
            # Decode image bytes using OpenCV imdecode
            nparr = np.frombuffer(image_source, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError("Failed to decode image from bytes.")
            return img

        elif isinstance(image_source, (str, Path)):
            # Load image from the filesystem path
            path_str = str(image_source)
            if not Path(path_str).exists():
                raise FileNotFoundError(f"Image file not found at path: {path_str}")
            img = cv2.imread(path_str, cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError(f"Failed to load image from path: {path_str}")
            return img

        else:
            raise TypeError("Unsupported image source type. Must be bytes, np.ndarray, str, or Path.")

    def convert_to_grayscale(self, image: np.ndarray) -> np.ndarray:
        """
        Step 1: Grayscale Conversion
        Converts a multi-channel (BGR/BGRA) image to a single-channel grayscale image.

        Explanation:
            Handwritten math expressions are defined by the ink strokes against a paper background.
            The colors of the ink or paper do not contain semantic mathematical value. By converting
            to grayscale, we reduce the image from 3 dimensions (Blue, Green, Red) to 1 dimension
            (intensity). This drops redundant color information, saves memory, and speeds up
            subsequent pixel-level computations (like thresholding and blurring) by a factor of 3.

        Args:
            image: 3-channel (BGR) or 4-channel (BGRA) image array.

        Returns:
            np.ndarray: Grayscale image (1 channel).
        """
        # If the image is already grayscale (2D array), return as is
        if len(image.shape) == 2:
            return image
        
        # Handle BGRA images (4 channels) or standard BGR (3 channels)
        if image.shape[2] == 4:
            return cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def remove_noise(self, gray_image: np.ndarray, method: str = "gaussian", kernel_size: int = 5) -> np.ndarray:
        """
        Step 2: Noise Removal
        Applies a smoothing filter to eliminate high-frequency noise while preserving stroke shapes.

        Explanation:
            Paper textures, wood fibers, scanned document lines, or camera sensor noise (like salt-and-pepper specks)
            can interfere with thresholding and feature extraction. We use smoothing filters to wash out
            these small imperfections.
            - Gaussian Blur: Convolves the image with a Gaussian kernel. It averages surrounding pixels
              weighted by distance, smoothing out high-frequency noise nicely.
            - Median Blur: Replaces each pixel value with the median of neighboring pixels. This is
              highly effective at eliminating salt-and-pepper noise and small specks while keeping
              expression stroke edges remarkably sharp.

        Args:
            gray_image: Single-channel grayscale image.
            method: The blurring technique to use ('gaussian' or 'median'). Defaults to 'gaussian'.
            kernel_size: Size of the filter kernel. Must be a positive odd integer.

        Returns:
            np.ndarray: Denoised grayscale image.
        """
        if kernel_size % 2 == 0 or kernel_size <= 0:
            raise ValueError("Kernel size must be a positive odd integer (e.g., 3, 5, 7).")

        if method == "gaussian":
            return cv2.GaussianBlur(gray_image, (kernel_size, kernel_size), 0)
        elif method == "median":
            return cv2.medianBlur(gray_image, kernel_size)
        else:
            # Fallback to Gaussian if unrecognized
            return cv2.GaussianBlur(gray_image, (kernel_size, kernel_size), 0)

    def enhance_contrast(self, gray_image: np.ndarray, clip_limit: float = 2.0, tile_grid_size: Tuple[int, int] = (8, 8)) -> np.ndarray:
        """
        Step 3: Contrast Enhancement
        Applies CLAHE (Contrast Limited Adaptive Histogram Equalization) to balance the image contrast.

        Explanation:
            Handwritten mathematical expressions can be written faintly (e.g., pencil or thin pen)
            or captured under poor, uneven lighting. Global histogram equalization tends to over-amplify
            the background noise and blow out highlights in brighter areas.
            CLAHE solves this by dividing the image into small local grids (tiles, e.g., 8x8), enhancing
            contrast within each tile independently, and then interpolating the boundaries. Additionally,
            it limits the contrast magnification to prevent highlighting background artifacts.

        Args:
            gray_image: Single-channel grayscale image.
            clip_limit: Threshold for contrast limiting. Higher values increase contrast.
            tile_grid_size: Size of grid for histogram equalization.

        Returns:
            np.ndarray: Contrast-enhanced grayscale image.
        """
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        return clahe.apply(gray_image)

    def adaptive_threshold(self, gray_image: np.ndarray, block_size: int = 11, constant_c: int = 2, invert: bool = True) -> np.ndarray:
        """
        Step 4: Adaptive Thresholding
        Binarizes the grayscale image to strictly separate ink strokes from the paper background.

        Explanation:
            Binarization converts the image into a binary format (pure black and pure white). This eliminates
            shading variations and isolates symbol strokes from the page.
            Using a global threshold (like Otsu's method) fails when shadows or light gradients exist across the page.
            Adaptive thresholding calculates a custom threshold for each pixel based on a small block neighborhood
            (of size block_size x block_size). 
            - ADAPTIVE_THRESH_GAUSSIAN_C calculates a Gaussian-weighted sum of the neighborhood minus constant_c.
            - If 'invert=True' (default), the output is inverted (THRESH_BINARY_INV) so that the ink strokes
              become white (255) and the background becomes black (0). Most neural network models prefer this sparse
              representation because zero-padding doesn't trigger convolution activation.

        Args:
            gray_image: Single-channel, contrast-enhanced grayscale image.
            block_size: Size of the local pixel neighborhood. Must be an odd number >= 3.
            constant_c: Constant subtracted from the mean or weighted mean.
            invert: If True, returns white text on black background. If False, returns black text on white background.

        Returns:
            np.ndarray: Binary image (values of strictly 0 and 255).
        """
        if block_size % 2 == 0 or block_size < 3:
            raise ValueError("Block size must be a positive odd integer greater than or equal to 3.")

        thresh_type = cv2.THRESH_BINARY_INV if invert else cv2.THRESH_BINARY
        
        return cv2.adaptiveThreshold(
            gray_image,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            thresh_type,
            block_size,
            constant_c
        )

    def resize_with_padding(self, image: np.ndarray, target_size: Tuple[int, int] = (640, 640), fill_value: int = 0) -> np.ndarray:
        """
        Step 5: Image Resizing with Aspect-Ratio-Preserving Padding (Letterboxing)
        Resizes the image to target dimensions while preventing visual distortion of the handwritten symbols.

        Explanation:
            Convolutional Neural Networks require fixed-size input tensors (e.g., 640x640). If we perform standard
            scaling, it will squeeze or stretch the image. For mathematical expressions, this is highly problematic:
            stretching a '+' might turn it into a elongated shape, a '-' might look like a box, or division lines
            and exponents may merge or change size.
            Instead, we:
            1. Calculate a scale factor that fits the image within the target boundary without stretching.
            2. Resize the image using cv2.INTER_AREA (which prevents aliasing artifacts when downscaling).
            3. Apply padding (using cv2.copyMakeBorder) with the appropriate background value (0 for black-background
               binarized images) to fill out the remaining space symmetrically, resulting in a perfect target resolution.

        Args:
            image: Input image (binary, grayscale, or color).
            target_size: Target (height, width) dimensions.
            fill_value: Pixel value used to pad the image (0 for black, 255 for white).

        Returns:
            np.ndarray: Resized and padded image.
        """
        h_target, w_target = target_size
        
        # Handle shape depending on dimensions
        if len(image.shape) == 3:
            h_orig, w_orig, channels = image.shape
            border_value = [fill_value] * channels
        else:
            h_orig, w_orig = image.shape
            border_value = fill_value

        # Calculate scale factor preserving aspect ratio
        scale = min(w_target / w_orig, h_target / h_orig)
        new_w = int(w_orig * scale)
        new_h = int(h_orig * scale)

        # Resize the image using area interpolation (optimal for downscaling)
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

        # Compute padding sizes (symmetrical padding)
        pad_top = (h_target - new_h) // 2
        pad_bottom = h_target - new_h - pad_top
        pad_left = (w_target - new_w) // 2
        pad_right = w_target - new_w - pad_left

        # Pad the image
        padded = cv2.copyMakeBorder(
            resized,
            pad_top,
            pad_bottom,
            pad_left,
            pad_right,
            cv2.BORDER_CONSTANT,
            value=border_value
        )
        
        return padded

    def normalize(self, image: np.ndarray, scale_to_one: bool = True) -> np.ndarray:
        """
        Step 6: Normalization
        Scales the intensity values of the image to a standardized range.

        Explanation:
            Neural network weights and activation functions (such as ReLU or Sigmoid) are optimized for small,
            controlled ranges. Inputting raw pixel values in [0, 255] can cause internal covariate shift,
            exploding/vanishing gradients, and extremely slow training convergence.
            By dividing the pixel values by 255.0, we normalize the range to [0.0, 1.0]. This aligns the
            inputs with typical neural network weight initializations.

        Args:
            image: Resized input image (typically np.uint8 format).
            scale_to_one: If True, divides values by 255.0 to scale in [0.0, 1.0].

        Returns:
            np.ndarray: Normalized image as float32 array.
        """
        float_img = image.astype(np.float32)
        if scale_to_one:
            float_img /= 255.0
        return float_img

    def preprocess(self, image_source: Union[bytes, np.ndarray, str, Path], **kwargs) -> np.ndarray:
        """
        Executes the entire image preprocessing pipeline.

        Args:
            image_source: Raw image bytes, filesystem path, or NumPy array.
            **kwargs: Configurable parameter overrides:
                - target_size (Tuple[int, int]): Size to resize to. Defaults to self.target_size.
                - noise_method (str): 'gaussian' or 'median'. Defaults to 'gaussian'.
                - noise_kernel (int): Size of blur kernel. Defaults to 5.
                - clahe_clip (float): Clip limit for CLAHE. Defaults to 2.0.
                - clahe_grid (Tuple[int, int]): Grid size for CLAHE. Defaults to (8, 8).
                - adaptive_block (int): Neighborhood size for adaptive threshold. Defaults to 11.
                - adaptive_c (int): Constant for adaptive threshold. Defaults to 2.
                - invert (bool): Whether to invert threshold result (white text on black bg). Defaults to True.
                - normalize (bool): Whether to scale values to [0.0, 1.0]. Defaults to True.

        Returns:
            np.ndarray: Model-ready normalized preprocessed image of shape (target_height, target_width)
                        or (target_height, target_width, 1) depending on downstream conventions.
        """
        # Load configurable parameters with defaults
        target_size = kwargs.get("target_size", self.target_size)
        noise_method = kwargs.get("noise_method", "gaussian")
        noise_kernel = kwargs.get("noise_kernel", 5)
        clahe_clip = kwargs.get("clahe_clip", 2.0)
        clahe_grid = kwargs.get("clahe_grid", (8, 8))
        adaptive_block = kwargs.get("adaptive_block", 11)
        adaptive_c = kwargs.get("adaptive_c", 2)
        invert = kwargs.get("invert", True)
        should_normalize = kwargs.get("normalize", True)

        # 1. Load and decode
        img = self.load_image(image_source)

        # 2. Grayscale conversion
        gray = self.convert_to_grayscale(img)

        # 3. Noise removal
        denoised = self.remove_noise(gray, method=noise_method, kernel_size=noise_kernel)

        # 4. Contrast enhancement
        enhanced = self.enhance_contrast(denoised, clip_limit=clahe_clip, tile_grid_size=clahe_grid)

        # 5. Adaptive thresholding (binarization)
        binary = self.adaptive_threshold(enhanced, block_size=adaptive_block, constant_c=adaptive_c, invert=invert)

        # 6. Aspect-ratio preserving resizing with padding
        # If the thresholding output was inverted, background is black (0), so pad with 0.
        # Otherwise background is white (255), so pad with 255.
        fill_val = 0 if invert else 255
        resized = self.resize_with_padding(binary, target_size=target_size, fill_value=fill_val)

        # 7. Normalization
        model_ready = self.normalize(resized, scale_to_one=should_normalize)

        # Ensure single channel dimension (H, W, 1) for neural networks that expect channel dimensions
        if len(model_ready.shape) == 2:
            model_ready = np.expand_dims(model_ready, axis=-1)

        return model_ready
