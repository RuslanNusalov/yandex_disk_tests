import pytest
import os
import shutil
from utils.api_client import YandexDiskClient
from utils.config import Config
from utils.helpers import generate_unique_name

@pytest.fixture(scope="session")
def api_client():
    """Фикстура для клиента API"""
    return YandexDiskClient()

@pytest.fixture(scope="session")
def test_prefix():
    """Фикстура для префикса тестовых ресурсов"""
    return Config.TEST_PREFIX

@pytest.fixture
def unique_folder_name(test_prefix):
    """Генерация уникального имени папки для каждого теста"""
    return generate_unique_name(test_prefix)

@pytest.fixture
def unique_file_name(test_prefix):
    """Генерация уникального имени файла для каждого теста"""
    return generate_unique_name(test_prefix)

@pytest.fixture
def test_folder(api_client, unique_folder_name, request):
    """Фикстура для создания и удаления тестовой папки"""
    # Создание папки перед тестом
    response = api_client.create_folder(unique_folder_name)
    
    # Проверяем, что папка создана
    if response.status_code not in [201, 409]:  # 409 = уже существует
        pytest.fail(f"Не удалось создать тестовую папку: {response.text}")
    
    yield unique_folder_name
    
    # Удаление папки после теста
    api_client.delete_resource(unique_folder_name, permanently=True)

@pytest.fixture
def test_file_path():
    """Путь к тестовому файлу"""
    return Config.TEST_FILE_PATH

@pytest.fixture
def test_file_content(test_file_path):
    """Содержимое тестового файла"""
    with open(test_file_path, 'r', encoding='utf-8') as f:
        return f.read()

@pytest.fixture(scope="session", autouse=True)
def cleanup_test_resources(request, api_client, test_prefix):
    """Очистка всех тестовых ресурсов после всех тестов"""
    def finalizer():
        """Удаление всех ресурсов с тестовым префиксом"""
        try:
            # Получаем список всех ресурсов
            response = api_client.get_resources_list('/', limit=1000)
            if response.status_code == 200:
                items = response.json().get('_embedded', {}).get('items', [])
                
                # Удаляем все ресурсы с тестовым префиксом
                for item in items:
                    path = item.get('path', '').split('/')[-1]
                    if path.startswith(test_prefix):
                        api_client.delete_resource(path, permanently=True)
        except Exception as e:
            print(f"Ошибка при очистке: {e}")
    
    request.addfinalizer(finalizer)
