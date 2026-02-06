import pytest
import requests
from utils.helpers import assert_status_code, wait_for_resource
from utils.config import Config

class TestFileOperations:
    """Тесты для операций с файлами"""
    
    @pytest.mark.smoke
    @pytest.mark.api
    @pytest.mark.post
    def test_upload_file(self, api_client, test_folder, test_file_path, test_file_content):
        """Тест: Загрузка файла (POST /resources/upload)"""
        file_name = f"{test_folder}/uploaded_file.txt"
        
        # Загружаем файл
        response = api_client.upload_file(file_name, test_file_path)
        assert response.status_code == 201, \
            f"Не удалось загрузить файл: {response.text}"
        
        # Проверяем, что файл появился
        assert wait_for_resource(api_client, file_name), \
            "Файл не появился после загрузки"
        
        # Проверяем метаданные файла
        metadata_response = api_client.get_metadata(file_name)
        assert_status_code(metadata_response, 200, "Не удалось получить метаданные файла")
        
        metadata = metadata_response.json()
        assert metadata['type'] == 'file', "Тип ресурса должен быть 'file'"
        assert metadata['name'] == 'uploaded_file.txt', "Имя файла не совпадает"
        assert metadata['mime_type'] == 'text/plain', "MIME тип должен быть text/plain"
    
    @pytest.mark.api
    @pytest.mark.get
    def test_download_file(self, api_client, test_folder, test_file_path, test_file_content):
        """Тест: Скачивание файла (GET /resources/download)"""
        file_name = f"{test_folder}/download_test.txt"
        
        # Загружаем файл
        api_client.upload_file(file_name, test_file_path)
        assert wait_for_resource(api_client, file_name)
        
        # Скачиваем файл
        download_path = 'data/downloaded_file.txt'
        success = api_client.download_file(file_name, download_path)
        
        assert success, "Не удалось скачать файл"
        
        # Проверяем содержимое
        with open(download_path, 'r', encoding='utf-8') as f:
            downloaded_content = f.read()
        
        assert downloaded_content == test_file_content, \
            "Содержимое скачанного файла не совпадает с оригиналом"
        
        # Очищаем временный файл
        import os
        if os.path.exists(download_path):
            os.remove(download_path)
    
    @pytest.mark.api
    @pytest.mark.post
    def test_upload_file_with_overwrite(self, api_client, test_folder, test_file_path):
        """Тест: Загрузка файла с перезаписью (overwrite=true)"""
        file_name = f"{test_folder}/overwrite_test.txt"
        
        # Загружаем файл первый раз
        response1 = api_client.upload_file(file_name, test_file_path)
        assert response1.status_code == 201
        
        # Загружаем файл второй раз с перезаписью
        response2 = api_client.upload_file(file_name, test_file_path, overwrite=True)
        assert response2.status_code == 201, \
            "Не удалось перезаписать файл"
        
        # Проверяем, что файл существует
        assert wait_for_resource(api_client, file_name), \
            "Файл не существует после перезаписи"
    
    @pytest.mark.api
    @pytest.mark.delete
    def test_delete_file(self, api_client, test_folder, test_file_path):
        """Тест: Удаление файла (DELETE /resources)"""
        file_name = f"{test_folder}/file_to_delete.txt"
        
        # Загружаем файл
        api_client.upload_file(file_name, test_file_path)
        assert wait_for_resource(api_client, file_name)
        
        # Удаляем файл
        response = api_client.delete_resource(file_name)
        assert_status_code(response, 204, "Не удалось удалить файл")
        
        # Проверяем, что файл удалён
        assert wait_for_resource(api_client, file_name, check_exists=False), \
            "Файл не был удалён"
        
        # Проверяем, что запрос метаданных возвращает 404
        metadata_response = api_client.get_metadata(file_name)
        assert_status_code(metadata_response, 404, "Удаленный файл всё ещё доступен")
    
    @pytest.mark.api
    @pytest.mark.post
    def test_move_rename_file(self, api_client, test_folder, test_file_path):
        """Тест: Перемещение/переименование файла (POST /resources/move)"""
        original_file = f"{test_folder}/original.txt"
        renamed_file = f"{test_folder}/renamed.txt"
        
        # Загружаем файл
        api_client.upload_file(original_file, test_file_path)
        assert wait_for_resource(api_client, original_file)
        
        # Переименовываем файл
        response = api_client.move_resource(original_file, renamed_file)
        assert_status_code(response, 201, "Не удалось переименовать файл")
        
        # Проверяем, что старый файл удалён
        old_metadata = api_client.get_metadata(original_file)
        assert old_metadata.status_code == 404, "Старый файл всё ещё существует"
        
        # Проверяем, что новый файл создан
        assert wait_for_resource(api_client, renamed_file), \
            "Новый файл не появился"
    
    @pytest.mark.api
    @pytest.mark.post
    def test_copy_file(self, api_client, test_folder, test_file_path):
        """Тест: Копирование файла (POST /resources/copy)"""
        original_file = f"{test_folder}/original.txt"
        copy_file = f"{test_folder}/copy.txt"
        
        # Загружаем файл
        api_client.upload_file(original_file, test_file_path)
        assert wait_for_resource(api_client, original_file)
        
        # Копируем файл
        response = api_client.copy_resource(original_file, copy_file)
        assert_status_code(response, 201, "Не удалось скопировать файл")
        
        # Проверяем, что копия существует
        assert wait_for_resource(api_client, copy_file), \
            "Копия файла не появилась"
        
        # Проверяем, что оба файла доступны
        original_metadata = api_client.get_metadata(original_file)
        copy_metadata = api_client.get_metadata(copy_file)
        
        assert original_metadata.status_code == 200, "Оригинальный файл недоступен"
        assert copy_metadata.status_code == 200, "Копия файла недоступна"
