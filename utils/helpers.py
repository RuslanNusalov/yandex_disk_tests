import time
from typing import Callable
from requests import Response

def wait_for_resource(client, path: str, timeout: int = 30, check_exists: bool = True) -> bool:
    """Ожидание появления/исчезновения ресурса"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        response = client.get_metadata(path)
        
        if check_exists and response.status_code == 200:
            return True
        elif not check_exists and response.status_code == 404:
            return True
        
        time.sleep(1)
    
    return False

def retry_on_failure(max_attempts: int = 3, delay: int = 2):
    """Декоратор для повторных попыток"""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    print(f"Попытка {attempt + 1} не удалась: {e}. Повтор через {delay} сек...")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

def generate_unique_name(prefix: str) -> str:
    """Генерация уникального имени с временной меткой"""
    import uuid
    return f"{prefix}{uuid.uuid4().hex[:8]}"

def assert_status_code(response: Response, expected_code: int, message: str = ""):
    """Проверка статус кода с информативным сообщением"""
    assert response.status_code == expected_code, \
        f"{message}\nExpected: {expected_code}, Got: {response.status_code}\nResponse: {response.text}"
