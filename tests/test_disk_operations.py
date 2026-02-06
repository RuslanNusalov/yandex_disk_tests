import pytest
from utils.helpers import assert_status_code

class TestDiskOperations:
    """Тесты для операций с диском"""
    
    @pytest.mark.smoke
    @pytest.mark.api
    @pytest.mark.get
    def test_get_disk_info(self, api_client):
        """Тест: Получение информации о диске (GET /)"""
        response = api_client.get_disk_info()
        
        assert_status_code(response, 200, "Не удалось получить информацию о диске")
        
        # Проверяем структуру ответа
        data = response.json()
        assert 'total_space' in data, "Отсутствует поле total_space"
        assert 'used_space' in data, "Отсутствует поле used_space"
        assert 'system_folders' in data, "Отсутствует поле system_folders"
        assert data['total_space'] > 0, "Общее пространство должно быть > 0"
        assert data['used_space'] >= 0, "Использованное пространство должно быть >= 0"
    
    @pytest.mark.api
    @pytest.mark.get
    def test_disk_quota_info(self, api_client):
        """Тест: Проверка информации о квоте диска"""
        response = api_client.get_disk_info()
        data = response.json()
        
        # Проверяем, что использованное пространство не превышает общее
        assert data['used_space'] <= data['total_space'], \
            "Использованное пространство не может превышать общее"
        
        # Проверяем процент использования
        usage_percent = (data['used_space'] / data['total_space']) * 100
        assert 0 <= usage_percent <= 100, "Процент использования должен быть в диапазоне 0-100"
