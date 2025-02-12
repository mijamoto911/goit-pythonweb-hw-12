from src.services.upload_file import UploadFileService


def test_upload_file():
    service = UploadFileService("cloud_name", "api_key", "api_secret")
    file_mock = type("FileMock", (), {"file": b"test_file"})()
    url = service.upload_file(file_mock, "testuser")
    assert "cloudinary" in url
