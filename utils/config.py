import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Конфигурация для тестов"""
    
    # API Configuration
    API_URL = os.getenv('YANDEX_DISK_API_URL', 'https://cloud-api.yandex.net/v1/disk')
    TOKEN = os.getenv('YANDEX_DISK_TOKEN')
    
    # Test Configuration
    TEST_PREFIX = os.getenv('TEST_PREFIX', 'test_yd_api_')
    TIMEOUT = 30
    
    # Test Data
    TEST_FILE_PATH = 'data/test_file.txt'
    TEST_IMAGE_PATH = 'data/test_image.png'
    
    @classmethod
    def get_headers(cls, include_content_type=True):
        """Возвращает заголовки для запросов"""
        if not cls.TOKEN:
            raise ValueError(
                "YANDEX_DISK_TOKEN не найден. "
                "Скопируйте .env.example в .env и добавьте ваш токен."
            )
        headers = {
            'Authorization': f'OAuth {cls.TOKEN}',
            'Accept': 'application/json'
        }
        if include_content_type:
            headers['Content-Type'] = 'application/json'
        return headers
