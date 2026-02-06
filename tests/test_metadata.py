import pytest
from utils.helpers import assert_status_code

class TestMetadata:
    """Тесты для работы с метаданными"""
    
    @pytest.mark.api
    @pytest.mark.get
    def test_get_file_metadata(self, api_client, test_folder, test_file_path):
        """Тест: Получение метаданных файла"""
        file_name = f"{test_folder}/metadata_test.txt"
        
        # Загружаем файл
        api_client.upload_file(file_name, test_file_path)
        
        # Получаем метаданные
        response = api_client.get_metadata(file_name)
        assert_status_code(response, 200, "Не удалось получить метаданные")
        
        metadata = response.json()
        
        # Проверяем обязательные поля
        assert 'type' in metadata, "Отсутствует поле type"
        assert 'name' in metadata, "Отсутствует поле name"
        assert 'path' in metadata, "Отсутствует поле path"
        assert 'created' in metadata, "Отсутствует поле created"
        assert 'modified' in metadata, "Отсутствует поле modified"
        assert 'size' in metadata, "Отсутствует поле size"
        
        # Проверяем значения
        assert metadata['type'] == 'file', "Тип должен быть 'file'"
        assert metadata['name'] == 'metadata_test.txt', "Неверное имя файла"
        assert metadata['size'] > 0, "Размер файла должен быть > 0"
    
    @pytest.mark.api
    @pytest.mark.get
    def test_get_folder_metadata(self, api_client, test_folder):
        """Тест: Получение метаданных папки"""
        response = api_client.get_metadata(test_folder)
        assert_status_code(response, 200, "Не удалось получить метаданные папки")
        
        metadata = response.json()
        
        # Проверяем обязательные поля
        assert 'type' in metadata, "Отсутствует поле type"
        assert 'name' in metadata, "Отсутствует поле name"
        assert 'path' in metadata, "Отсутствует поле path"
        assert 'created' in metadata, "Отсутствует поле created"
        
        # Проверяем значения
        assert metadata['type'] == 'dir', "Тип должен быть 'dir'"
        assert metadata['name'] == test_folder, "Неверное имя папки"
    
    @pytest.mark.api
    @pytest.mark.get
    def test_get_nonexistent_resource_metadata(self, api_client):
        """Тест: Получение метаданных несуществующего ресурса"""
        nonexistent_path = f"{Config.TEST_PREFIX}nonexistent_{Config.TEST_PREFIX}"
        
        response = api_client.get_metadata(nonexistent_path)
        assert_status_code(response, 404, "Несуществующий ресурс должен возвращать 404")
