"""
Реалізація алгоритму планування NLOOK (N-Level LOOK).

Використовує кілька черг обмеженої довжини для покращення відгуку системи
та запобігання голодуванню запитів.
"""

from collections import deque
from typing import Optional
from schedulers.base import IOScheduler
from core.events import IORequest
from core.disk import HardDisk


class NLOOKScheduler(IOScheduler):
    """
    Планувальник за алгоритмом NLOOK (N-Level LOOK).
    
    Підтримує кілька черг запитів з обмеженою довжиною. Нові запити
    додаються до останньої черги, а опрацювання відбувається завжди
    з найстарішої черги у напрямку зростання номерів доріжок.
    
    Атрибути:
        queues: Список черг запитів
        max_queue_length: Максимальна довжина однієї черги
        direction_increasing: Напрямок опрацювання (завжди True для NLOOK)
    """
    
    def __init__(self, max_queue_length: int = 5):
        """
        Ініціалізує NLOOK планувальник.
        
        Args:
            max_queue_length: Максимальна кількість запитів в одній черзі
        """
        super().__init__("NLOOK")
        self.queues = [deque()]
        self.max_queue_length = max_queue_length
        self.direction_increasing = True
    
    def add_request(self, request: IORequest, simulator):
        """
        Додає запит до останньої черги або створює нову при переповненні.
        
        Args:
            request: Запит для додавання
            simulator: Об'єкт симулятора для логування
        """
        # Якщо всі черги порожні, створюємо нову
        if not self.queues:
            self.queues.append(deque())
        
        if len(self.queues[-1]) >= self.max_queue_length:
            self.queues.append(deque())
            if simulator.verbose:
                simulator.log(f"IO Scheduler (NLOOK): created new queue (total: {len(self.queues)})")
        
        self.queues[-1].append(request)
        if simulator.verbose:
            simulator.log(f"IO Scheduler (NLOOK): added request {request.request_type.value} "
                         f"sector {request.sector} to queue {len(self.queues)-1}")
    
    def get_next_request(self, disk: HardDisk, simulator) -> Optional[IORequest]:
        """
        Вибирає запит із найстарішої черги у напрямку зростання доріжок.
        
        Args:
            disk: Модель диска для визначення поточної позиції
            simulator: Об'єкт симулятора для логування
        
        Returns:
            Оптимальний запит або перший запит черги
        """
        self.queues = [q for q in self.queues if q]
        
        if not self.queues:
            return None
        
        current_queue = self.queues[0]
        sorted_queue = sorted(current_queue, key=lambda r: r.get_track(disk.sectors_per_track))
        current_track = disk.current_track
        
        selected = None
        for req in sorted_queue:
            req_track = req.get_track(disk.sectors_per_track)
            if req_track >= current_track:
                selected = req
                break
        
        if selected is None and sorted_queue:
            selected = sorted_queue[0]
            if simulator.verbose:
                simulator.log(f"IO Scheduler (NLOOK): no suitable request, taking from start")
        
        if selected:
            current_queue.remove(selected)
            if simulator.verbose:
                simulator.log(f"IO Scheduler (NLOOK): selected sector {selected.sector} from queue 0")
            
            if not current_queue:
                self.queues.pop(0)
                if self.queues and simulator.verbose:
                    simulator.log(f"IO Scheduler (NLOOK): queue 0 processed, "
                                f"switching to next queue")
        
        return selected
    
    def is_empty(self) -> bool:
        """Перевіряє чи всі черги порожні"""
        return not any(self.queues)