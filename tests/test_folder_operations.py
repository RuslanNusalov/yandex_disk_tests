import pytest
from utils.helpers import assert_status_code, wait_for_resource
from utils.config import Config  # ДОБАВЛЕН ИМПОРТ

class TestFolderOperations:
    """Тесты для операций с папками"""
    
    @pytest.mark.smoke
    @pytest.mark.api
    @pytest.mark.put
    def test_create_folder(self, api_client, unique_folder_name):
        """Тест: Создание папки (PUT /resources)"""
        response = api_client.create_folder(unique_folder_name)
        
        # 201 = создано, 409 = уже существует (тоже OK для наших целей)
        assert response.status_code in [201, 409], \
            f"Не удалось создать папку. Status: {response.status_code}, Response: {response.text}"
        
        # Проверяем, что папка действительно создана
        assert wait_for_resource(api_client, unique_folder_name), \
            "Папка не появилась в течение ожидаемого времени"
        
        # Проверяем метаданные созданной папки
        metadata_response = api_client.get_metadata(unique_folder_name)
        assert_status_code(metadata_response, 200, "Не удалось получить метаданные папки")
        
        metadata = metadata_response.json()
        assert metadata['type'] == 'dir', "Тип ресурса должен быть 'dir'"
        assert metadata['name'] == unique_folder_name, "Имя папки не совпадает"
    
    @pytest.mark.api
    @pytest.mark.get
    def test_get_folder_contents(self, api_client, test_folder):
        """Тест: Получение содержимого папки (GET /resources)"""
        response = api_client.get_resources_list(test_folder)
        
        assert_status_code(response, 200, "Не удалось получить содержимое папки")
        
        data = response.json()
        assert '_embedded' in data, "Отсутствует поле _embedded"
        assert 'items' in data['_embedded'], "Отсутствует поле items"
        
        # Проверяем, что папка пустая (только что создана)
        assert len(data['_embedded']['items']) == 0, "Новая папка должна быть пустой"
    
    @pytest.mark.api
    @pytest.mark.put
    def test_create_nested_folder(self, api_client, test_folder):
        """Тест: Создание вложенной папки"""
        nested_folder = f"{test_folder}/nested_folder"
        
        response = api_client.create_folder(nested_folder)
        assert response.status_code in [201, 409], \
            f"Не удалось создать вложенную папку: {response.text}"
        
        # Проверяем, что вложенная папка существует
        assert wait_for_resource(api_client, nested_folder), \
            "Вложенная папка не появилась"
        
        # Проверяем, что родительская папка содержит вложенную
        parent_contents = api_client.get_resources_list(test_folder)
        items = parent_contents.json()['_embedded']['items']
        assert any(item['name'] == 'nested_folder' for item in items), \
            "Вложенная папка не отображается в родительской"
    
    @pytest.mark.api
    @pytest.mark.delete
    def test_delete_folder(self, api_client, unique_folder_name):
        """Тест: Удаление папки (DELETE /resources)"""
        # Создаем папку
        create_response = api_client.create_folder(unique_folder_name)
        assert create_response.status_code in [201, 409]
        
        # Удаляем папку
        delete_response = api_client.delete_resource(unique_folder_name)
        assert_status_code(delete_response, 204, "Не удалось удалить папку")
        
        # Проверяем, что папка удалена
        assert wait_for_resource(api_client, unique_folder_name, check_exists=False), \
            "Папка не была удалена"
        
        # Проверяем, что запрос метаданных возвращает 404
        metadata_response = api_client.get_metadata(unique_folder_name)
        assert_status_code(metadata_response, 404, "Удаленная папка всё ещё доступна")
    
    @pytest.mark.api
    @pytest.mark.post
    def test_move_rename_folder(self, api_client, test_folder):
        """Тест: Перемещение/переименование папки (POST /resources/move)"""
        # ИСПРАВЛЕНО: используем префикс из конфигурации правильно
        new_folder_name = f"renamed_{test_folder}"  # Убран дублирующийся префикс
        
        response = api_client.move_resource(test_folder, new_folder_name)
        assert_status_code(response, 201, "Не удалось переместить/переименовать папку")
        
        # Проверяем, что старая папка удалена
        old_metadata = api_client.get_metadata(test_folder)
        assert old_metadata.status_code == 404, "Старая папка всё ещё существует"
        
        # Проверяем, что новая папка создана
        assert wait_for_resource(api_client, new_folder_name), \
            "Новая папка не появилась"
        
        # Очищаем
        api_client.delete_resource(new_folder_name, permanently=True)
    
    @pytest.mark.api
    @pytest.mark.post
    def test_copy_folder(self, api_client, test_folder):
        """Тест: Копирование папки (POST /resources/copy)"""
        copy_folder_name = f"{test_folder}_copy"
        
        # Создаем файл в исходной папке для проверки копирования содержимого
        test_file = f"{test_folder}/test.txt"
        with open('data/test_file.txt', 'r', encoding='utf-8') as f:
            content = f.read().encode('utf-8')
        
        upload_link = api_client.get_upload_link(test_file)
        requests.put(upload_link, data=content)
        
        # Копируем папку
        response = api_client.copy_resource(test_folder, copy_folder_name)
        assert_status_code(response, 201, "Не удалось скопировать папку")
        
        # Проверяем, что копия существует
        assert wait_for_resource(api_client, copy_folder_name), \
            "Копия папки не появилась"
        
        # Проверяем, что в копии есть файл
        copy_contents = api_client.get_resources_list(copy_folder_name)
        items = copy_contents.json()['_embedded']['items']
        assert any(item['name'] == 'test.txt' for item in items), \
            "Файл не скопировался вместе с папкой"
        
        # Очищаем
        api_client.delete_resource(copy_folder_name, permanently=True)
