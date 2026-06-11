import pytest
import numpy as np
import cv2
from app.services.image_preprocessing import ImagePreprocessingService


@pytest.fixture
def preprocessing_service():
    return ImagePreprocessingService(target_size=(640, 640))


@pytest.fixture
def dummy_color_image():
    # Create a 200x400 BGR dummy image with a white background and some black shapes/lines
    # (resembling handwritten text)
    img = np.ones((200, 400, 3), dtype=np.uint8) * 255
    # Draw some shapes (lines/circles) to represent strokes
    cv2.line(img, (50, 50), (150, 150), (0, 0, 0), thickness=5)
    cv2.circle(img, (250, 100), 40, (0, 0, 0), thickness=3)
    return img


def test_load_image_numpy(preprocessing_service, dummy_color_image):
    loaded = preprocessing_service.load_image(dummy_color_image)
    assert np.array_equal(loaded, dummy_color_image)
    # Check invalid array
    with pytest.raises(ValueError):
        preprocessing_service.load_image(np.array([]))


def test_load_image_bytes(preprocessing_service, dummy_color_image):
    # Encode dummy image to jpeg bytes
    _, encoded = cv2.imencode(".jpg", dummy_color_image)
    image_bytes = encoded.tobytes()

    loaded = preprocessing_service.load_image(image_bytes)
    assert loaded is not None
    assert len(loaded.shape) == 3
    assert loaded.shape[2] == 3


def test_convert_to_grayscale(preprocessing_service, dummy_color_image):
    gray = preprocessing_service.convert_to_grayscale(dummy_color_image)
    assert len(gray.shape) == 2
    assert gray.shape[0] == dummy_color_image.shape[0]
    assert gray.shape[1] == dummy_color_image.shape[1]

    # Test passing an already grayscale image
    already_gray = np.zeros((100, 100), dtype=np.uint8)
    assert preprocessing_service.convert_to_grayscale(already_gray) is already_gray


def test_remove_noise(preprocessing_service):
    # Create a noisy image
    np.random.seed(42)
    base_img = np.ones((100, 100), dtype=np.uint8) * 128
    noise = np.random.normal(0, 15, base_img.shape).astype(np.int16)
    noisy_img = np.clip(base_img + noise, 0, 255).astype(np.uint8)

    # Denoise with Gaussian
    denoised_gaussian = preprocessing_service.remove_noise(noisy_img, method="gaussian", kernel_size=5)
    assert denoised_gaussian.shape == noisy_img.shape
    # Standard deviation should have decreased
    assert np.std(denoised_gaussian) < np.std(noisy_img)

    # Denoise with Median
    denoised_median = preprocessing_service.remove_noise(noisy_img, method="median", kernel_size=5)
    assert denoised_median.shape == noisy_img.shape

    # Check kernel size validation
    with pytest.raises(ValueError):
        preprocessing_service.remove_noise(noisy_img, kernel_size=4)
    with pytest.raises(ValueError):
        preprocessing_service.remove_noise(noisy_img, kernel_size=-1)


def test_enhance_contrast(preprocessing_service):
    # Low contrast grayscale image
    low_contrast = np.ones((100, 100), dtype=np.uint8) * 100
    # Add a small gradient/variation
    low_contrast[30:70, 30:70] = 110

    enhanced = preprocessing_service.enhance_contrast(low_contrast, clip_limit=3.0)
    assert enhanced.shape == low_contrast.shape
    # Dynamic range should increase
    assert (enhanced.max() - enhanced.min()) > (low_contrast.max() - low_contrast.min())


def test_adaptive_threshold(preprocessing_service):
    # Image with gradient background and dark drawing
    gradient = np.zeros((100, 100), dtype=np.uint8)
    for i in range(100):
        gradient[i, :] = 100 + i  # lighting gradient from top to bottom
    # Draw a black line (representing ink)
    cv2.line(gradient, (10, 50), (90, 50), 0, thickness=4)

    # Run adaptive thresholding (inverted: white drawing on black background)
    binary = preprocessing_service.adaptive_threshold(gradient, block_size=11, constant_c=2, invert=True)
    assert binary.shape == gradient.shape
    # Check that it's strictly binary (0 and 255 values only)
    unique_vals = set(np.unique(binary))
    assert unique_vals.issubset({0, 255})
    
    # The line at row 50 should be white (255)
    assert np.any(binary[48:53, :] == 255)

    # Test invalid block size
    with pytest.raises(ValueError):
        preprocessing_service.adaptive_threshold(gradient, block_size=10)


def test_resize_with_padding(preprocessing_service):
    # 200 x 400 input, target 640 x 640
    img = np.ones((200, 400), dtype=np.uint8) * 255
    target_size = (640, 640)
    
    resized = preprocessing_service.resize_with_padding(img, target_size=target_size, fill_value=0)
    assert resized.shape == target_size
    
    # Since aspect ratio is preserved:
    # 400 scaled to 640 -> scale factor is 640 / 400 = 1.6
    # 200 scaled by 1.6 -> 320
    # Thus, the height should be 320, padded at top/bottom by (640-320)/2 = 160 pixels
    # Verify that the border values are indeed 0 (padded area)
    assert np.all(resized[0:150, :] == 0)
    assert np.all(resized[490:640, :] == 0)
    # The content area should have some 255 values from the original image
    assert np.any(resized[160:480, :] == 255)


def test_normalize(preprocessing_service):
    img = np.ones((100, 100), dtype=np.uint8) * 255
    normalized = preprocessing_service.normalize(img, scale_to_one=True)
    assert normalized.dtype == np.float32
    assert normalized.max() == 1.0
    assert normalized.min() == 1.0

    not_scaled = preprocessing_service.normalize(img, scale_to_one=False)
    assert not_scaled.dtype == np.float32
    assert not_scaled.max() == 255.0


def test_end_to_end_pipeline(preprocessing_service, dummy_color_image):
    processed = preprocessing_service.preprocess(
        dummy_color_image,
        target_size=(640, 640),
        noise_method="median",
        noise_kernel=3,
        clahe_clip=2.0,
        adaptive_block=11,
        adaptive_c=2,
        invert=True,
        normalize=True
    )
    
    # Output should have channel dimension (640, 640, 1)
    assert processed.shape == (640, 640, 1)
    assert processed.dtype == np.float32
    assert processed.max() <= 1.0
    assert processed.min() >= 0.0
