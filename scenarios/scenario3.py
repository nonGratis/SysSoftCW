

"""
Сценарій для тестування ефективності буферного кешу.

Включає процеси з повторними зверненнями до одних і тих же секторів
для демонстрації переваг кешування.
"""

from typing import List
from core.process import Process
from core.events import RequestType
from config import SystemConfig


def create_cache_test_scenario(config: SystemConfig) -> List[Process]:
    """
    Створює процеси з повторними зверненнями для тестування кешу.
    
    Цей сценарій демонструє ефективність буферного кешу LRU з двома сегментами
    за наявності локальності звернень.
    
    Args:
        config: Конфігурація системи
    
    Returns:
        Список процесів із частими повторними зверненнями
    """
    processes = []
    
    processes.append(Process(1, [
        (RequestType.READ, 100),
        (RequestType.READ, 200),
        (RequestType.READ, 100),
        (RequestType.READ, 200),
        (RequestType.READ, 300),
        (RequestType.READ, 100),
        (RequestType.WRITE, 200),
        (RequestType.READ, 100),
    ]))
    
    if config.num_processes >= 2:
        processes.append(Process(2, [
            (RequestType.READ, 500),
            (RequestType.READ, 600),
            (RequestType.READ, 500),
            (RequestType.READ, 600),
            (RequestType.READ, 500),
        ]))
    
    if config.num_processes >= 3:
        processes.append(Process(3, [
            (RequestType.READ, 1000),
            (RequestType.WRITE, 1000),
            (RequestType.READ, 1100),
            (RequestType.READ, 1000),
            (RequestType.READ, 1100),
        ]))
    
    return processes