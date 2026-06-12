def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_predict_uses_pix2tex_workflow(client):
    from io import BytesIO
    from PIL import Image

    image = Image.new("RGB", (120, 48), "white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    response = client.post(
        "/api/v1/predict",
        files={"image": ("equation.png", buffer.getvalue(), "image/png")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["latex"] == r"x^2 + y"
    assert data["prediction_id"]
    assert data["image_path"].startswith("/uploads/predictions/")
    assert data["confidence_source"] == "placeholder_success_default"
    assert "symbols_detected" not in data


def test_model_status_reports_pix2tex(client):
    response = client.get("/api/v1/model/status")

    assert response.status_code == 200
    assert response.json()["engine"] == "pix2tex"
