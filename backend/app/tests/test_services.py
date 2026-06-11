def test_yolo_service():
    from app.services.yolo_service import YoloService
    service = YoloService()
    assert service.get_config()["framework"] == "ultralytics YOLOv11"
