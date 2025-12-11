"""
Базовий клас для планувальників введення-виведення.

Визначає загальний інтерфейс для всіх алгоритмів планування та
містить базову функціональність управління чергою запитів.
"""

from collections import deque
from typing import Optional
from core.events import IORequest
from core.disk import HardDisk


class IOScheduler:
    """
    Базовий клас для планувальників введення-виведення.
    
    Визначає стандартний інтерфейс, який повинні реалізувати всі
    конкретні алгоритми планування запитів до диска.
    
    Атрибути:
        name: Назва алгоритму планування
        queue: Черга запитів введення-виведення
    """
    
    def __init__(self, name: str):
        """
        Ініціалізує планувальник із заданою назвою.
        
        Args:
            name: Назва алгоритму для ідентифікації та логування
        """
        self.name = name
        self.queue = deque()
    
    def add_request(self, request: IORequest, simulator):
        """
        Додає новий запит до черги планувальника.
        
        Args:
            request: Запит введення-виведення для додавання
            simulator: Об'єкт симулятора для логування подій
        """
        self.queue.append(request)
        simulator.log(f"IO Scheduler ({self.name}): added request "
                     f"{request.request_type.value} sector {request.sector} "
                     f"from process {request.process_id}")
    
    def get_next_request(self, disk: HardDisk, simulator) -> Optional[IORequest]:
        """
        Вибирає наступний запит для виконання контролером диска.
        
        Цей метод повинен бути перевизначений у підкласах для реалізації
        специфічної логіки алгоритму планування.
        
        Args:
            disk: Об'єкт моделі жорсткого диска для доступу до параметрів
            simulator: Об'єкт симулятора для логування
        
        Returns:
            Наступний запит для виконання або None якщо черга порожня
        
        Raises:
            NotImplementedError: Якщо метод не реалізований у підкласі
        """
        raise NotImplementedError("Method must be implemented in subclass")
    
    def is_empty(self) -> bool:
        """
        Перевіряє чи черга запитів порожня.
        
        Returns:
            True якщо черга не містить запитів, інакше False
        """
        return len(self.queue) == 0