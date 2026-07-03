from PIL import Image, ImageDraw


def test_pix2tex_service_health_and_prediction():
    from app.services.pix2tex_service import Pix2TexOCRService

    service = Pix2TexOCRService()
    service.initialize()

    image = Image.new("RGB", (80, 32), "white")
    ImageDraw.Draw(image).line((10, 16, 60, 16), fill="black", width=3)

    result = service.predict(image)

    assert service.health_status()["engine"] == "pix2tex"
    assert service.is_loaded is True
    assert result.latex == r"x^2 + y"
    assert result.confidence_source == "placeholder_success_default"
