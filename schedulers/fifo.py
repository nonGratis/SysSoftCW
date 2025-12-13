"""
Реалізація алгоритму планування FIFO (First In First Out).

Найпростіший алгоритм планування, що опрацьовує запити в порядку їх надходження
без урахування поточної позиції головки диска.
"""

from typing import Optional
from schedulers.base import IOScheduler
from core.events import IORequest
from core.disk import HardDisk


class FIFOScheduler(IOScheduler):
    """
    Планувальник за алгоритмом FIFO (First In First Out).
    
    Обробляє запити в порядку їх надходження до черги без оптимізації
    переміщень головки диска. Забезпечує справедливість та передбачуваність,
    але може призводити до неоптимального часу виконання операцій.
    """
    
    def __init__(self):
        """Ініціалізує FIFO планувальник."""
        super().__init__("FIFO")
    
    def get_next_request(self, disk: HardDisk, simulator) -> Optional[IORequest]:
        """
        Повертає перший запит із черги.
        
        Args:
            disk: Модель жорсткого диска (не використовується у FIFO)
            simulator: Об'єкт симулятора для логування
        
        Returns:
            Найстаріший запит у черзі або None якщо черга порожня
        """
        if self.queue:
            request = self.queue.popleft()
            if simulator.verbose:
                simulator.log(f"IO Scheduler (FIFO): selected request sector {request.sector}")
            return request
        return None