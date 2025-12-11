"""
Стандартний сценарій з різноманітними зверненнями до секторів.

Демонструє роботу системи з процесами, що виконують змішані операції
читання та запису до різних областей диска.
"""

from typing import List
from core.process import Process
from core.events import RequestType
from config import SystemConfig


def create_default_scenario(config: SystemConfig) -> List[Process]:
    """
    Створює стандартний набір процесів із різноманітними зверненнями.
    
    Сценарій включає процеси із зверненнями до різних областей диска,
    включаючи повторні звернення для демонстрації роботи буферного кешу.
    
    Args:
        config: Конфігурація системи
    
    Returns:
        Список об'єктів Process для виконання
    """
    processes = []
    
    processes.append(Process(1, [
        (RequestType.READ, 1250),
        (RequestType.WRITE, 1700),
        (RequestType.READ, 1250),
        (RequestType.READ, 500),
    ]))
    
    if config.num_processes >= 2:
        processes.append(Process(2, [
            (RequestType.READ, 5000),
            (RequestType.READ, 5100),
            (RequestType.WRITE, 3000),
        ]))
    
    if config.num_processes >= 3:
        processes.append(Process(3, [
            (RequestType.READ, 2500),
            (RequestType.WRITE, 2600),
            (RequestType.READ, 2500),
        ]))
    
    return processes
