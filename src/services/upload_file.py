import cloudinary
import cloudinary.uploader


class UploadFileService:
    """
    Сервіс для завантаження файлів у Cloudinary.

    :param cloud_name: Назва хмарного сервера Cloudinary.
    :type cloud_name: str
    :param api_key: API-ключ Cloudinary.
    :type api_key: str
    :param api_secret: Секретний API-ключ Cloudinary.
    :type api_secret: str
    """

    def __init__(self, cloud_name: str, api_key: str, api_secret: str):
        """
        Ініціалізація сервісу Cloudinary.

        :param cloud_name: Назва хмарного сервера Cloudinary.
        :param api_key: API-ключ Cloudinary.
        :param api_secret: Секретний API-ключ Cloudinary.
        """
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True,
        )

    @staticmethod
    def upload_file(file, username: str) -> str:
        """
        Завантажує файл у Cloudinary та повертає URL.

        :param file: Файл для завантаження.
        :type file: UploadFile
        :param username: Ім'я користувача (використовується для public_id).
        :type username: str
        :return: URL зображення, обробленого Cloudinary.
        :rtype: str
        """
        public_id = f"RestApp/{username}"
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop="fill", version=r.get("version")
        )
        return src_url
