import requests
from typing import Optional
from utils.config import Config

class YandexDiskClient:
    """Клиент для работы с Яндекс.Диском API"""
    
    def __init__(self):
        self.base_url = Config.API_URL
        self.timeout = Config.TIMEOUT
    
    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Базовый метод для выполнения запросов"""
        url = f"{self.base_url}{endpoint}"
        
        # Заголовки: Content-Type только для запросов с телом
        include_content_type = method in ['POST', 'PUT', 'PATCH']
        kwargs['headers'] = Config.get_headers(include_content_type=include_content_type)
        kwargs['timeout'] = self.timeout
        
        response = requests.request(method, url, **kwargs)
        return response
    
    # ========== DISK INFO ==========
    def get_disk_info(self) -> requests.Response:
        """GET / - Получить информацию о диске"""
        return self._request('GET', '/')
    
    # ========== RESOURCES ==========
    def create_folder(self, path: str) -> requests.Response:
        """PUT /resources - Создать папку
        path: путь относительно корня диска (например, 'test_folder')
        """
        params = {'path': f'disk:/{path}'}
        return self._request('PUT', '/resources', params=params)
    
    def delete_resource(self, path: str, permanently: bool = False) -> requests.Response:
        """DELETE /resources - Удалить ресурс"""
        params = {'path': f'disk:/{path}', 'permanently': permanently}
        return self._request('DELETE', '/resources', params=params)
    
    def get_metadata(self, path: str) -> requests.Response:
        """GET /resources - Получить метаданные ресурса"""
        params = {'path': f'disk:/{path}'}
        return self._request('GET', '/resources', params=params)
    
    def get_resources_list(self, path: str = '/', limit: int = 20) -> requests.Response:
        """GET /resources - Получить список ресурсов"""
        params = {'path': f'disk:/{path}', 'limit': limit}
        return self._request('GET', '/resources', params=params)
    
    def move_resource(self, from_path: str, to_path: str, overwrite: bool = False) -> requests.Response:
        """POST /resources/move - Переместить/переименовать ресурс"""
        params = {
            'from': f'disk:/{from_path}',
            'path': f'disk:/{to_path}',
            'overwrite': overwrite
        }
        return self._request('POST', '/resources/move', params=params)
    
    def copy_resource(self, from_path: str, to_path: str, overwrite: bool = False) -> requests.Response:
        """POST /resources/copy - Копировать ресурс"""
        params = {
            'from': f'disk:/{from_path}',
            'path': f'disk:/{to_path}',
            'overwrite': overwrite
        }
        return self._request('POST', '/resources/copy', params=params)
    
    # ========== UPLOAD ==========
    def get_upload_link(self, path: str, overwrite: bool = False) -> Optional[str]:
        """GET /resources/upload - Получить ссылку для загрузки файла"""
        params = {'path': f'disk:/{path}', 'overwrite': overwrite}
        response = self._request('GET', '/resources/upload', params=params)
        
        if response.status_code == 200:
            return response.json().get('href')
        return None
    
    def upload_file(self, path: str, file_path: str, overwrite: bool = False) -> requests.Response:
        """Загрузить файл на диск"""
        upload_link = self.get_upload_link(path, overwrite)
        
        if not upload_link:
            raise ValueError(f"Не удалось получить ссылку для загрузки: {path}")
        
        # Загрузка файла: БЕЗ заголовка Content-Type (автоопределение)
        with open(file_path, 'rb') as f:
            response = requests.put(upload_link, data=f, timeout=self.timeout)
        
        return response
    
    # ========== DOWNLOAD ==========
    def get_download_link(self, path: str) -> Optional[str]:
        """GET /resources/download - Получить ссылку для скачивания файла"""
        params = {'path': f'disk:/{path}'}
        response = self._request('GET', '/resources/download', params=params)
        
        if response.status_code == 200:
            return response.json().get('href')
        return None
    
    def download_file(self, path: str, save_path: str) -> bool:
        """Скачать файл с диска"""
        download_link = self.get_download_link(path)
        
        if not download_link:
            return False
        
        response = requests.get(download_link, timeout=self.timeout)
        
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return True
        return False
    
    # ========== PUBLISH ==========
    def publish_resource(self, path: str) -> requests.Response:
        """PUT /resources/publish - Опубликовать ресурс"""
        params = {'path': f'disk:/{path}'}
        return self._request('PUT', '/resources/publish', params=params)
    
    def unpublish_resource(self, path: str) -> requests.Response:
        """PUT /resources/unpublish - Отменить публикацию"""
        params = {'path': f'disk:/{path}'}
        return self._request('PUT', '/resources/unpublish', params=params)
