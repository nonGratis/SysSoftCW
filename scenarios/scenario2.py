

"""
Сценарії з послідовними та випадковими зверненнями.

Створює процеси із специфічними патернами доступу для аналізу
ефективності різних алгоритмів планування.
"""

import random
from typing import List
from core.process import Process
from core.events import RequestType
from config import SystemConfig


def create_sequential_scenario(config: SystemConfig) -> List[Process]:
    """
    Створює процеси з послідовними зверненнями до секторів.
    
    Цей сценарій демонструє оптимальну роботу алгоритмів LOOK, NLOOK
    оскільки звернення розташовані послідовно на диску.
    
    Args:
        config: Конфігурація системи
    
    Returns:
        Список процесів із послідовними зверненнями
    """
    processes = []
    
    base_sector = 1000
    for i in range(config.num_processes):
        operations = []
        start = base_sector + i * 2000
        
        for j in range(10):
            sector = start + j * 100
            op_type = RequestType.READ if j % 2 == 0 else RequestType.WRITE
            operations.append((op_type, sector))
        
        processes.append(Process(i + 1, operations))
    
    return processes


def create_random_scenario(config: SystemConfig) -> List[Process]:
    """
    Створює процеси з випадковими зверненнями по всьому диску.
    
    Найбільш складний сценарій для планувальників, демонструє перевагу
    алгоритмів сортування над FIFO.
    
    Args:
        config: Конфігурація системи
    
    Returns:
        Список процесів із випадковими зверненнями
    """
    processes = []
    total_sectors = config.num_tracks * config.sectors_per_track
    
    random.seed(42)
    
    for i in range(config.num_processes):
        operations = []
        
        for j in range(15):
            sector = random.randint(0, total_sectors - 1)
            op_type = random.choice([RequestType.READ, RequestType.WRITE])
            operations.append((op_type, sector))
        
        processes.append(Process(i + 1, operations))
    
    return processes
