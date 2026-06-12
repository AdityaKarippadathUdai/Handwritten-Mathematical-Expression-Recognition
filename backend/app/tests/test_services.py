from PIL import Image


def test_pix2tex_service_health_and_prediction():
    from app.services.pix2tex_service import Pix2TexOCRService

    service = Pix2TexOCRService()
    service.initialize()

    result = service.predict(Image.new("RGB", (80, 32), "white"))

    assert service.health_status()["engine"] == "pix2tex"
    assert service.is_loaded is True
    assert result.latex == r"x^2 + y"
    assert result.confidence_source == "placeholder_success_default"
