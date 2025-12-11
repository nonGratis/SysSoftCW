"""
Реалізація алгоритму планування LOOK.

Алгоритм сортує запити та обробляє їх у напрямку руху головки диска,
мінімізуючи загальну відстань переміщення.
"""

from typing import Optional
from schedulers.base import IOScheduler
from core.events import IORequest
from core.disk import HardDisk


class LOOKScheduler(IOScheduler):
    """
    Планувальник за алгоритмом LOOK.
    
    Опрацьовує запити в напрямку зростання або зменшення номерів доріжок.
    При досягненні кінця черги у поточному напрямку змінює напрямок руху.
    Обмежує кількість послідовних звернень до однієї доріжки для запобігання
    голодуванню інших запитів.
    
    Атрибути:
        max_track_accesses: Максимальна кількість послідовних звернень до однієї доріжки
        direction_increasing: Поточний напрямок руху (True - зростання номерів)
        current_track_accesses: Лічильник звернень до поточної доріжки
        last_track: Номер останньої обробленої доріжки
    """
    
    def __init__(self, max_track_accesses: int = 10):
        """
        Ініціалізує LOOK планувальник.
        
        Args:
            max_track_accesses: Максимальна кількість звернень до однієї доріжки
        """
        super().__init__("LOOK")
        self.max_track_accesses = max_track_accesses
        self.direction_increasing = True
        self.current_track_accesses = 0
        self.last_track = None
    
    def get_next_request(self, disk: HardDisk, simulator) -> Optional[IORequest]:
        """
        Вибирає наступний запит у поточному напрямку руху головки.
        
        Args:
            disk: Модель жорсткого диска для доступу до поточної позиції
            simulator: Об'єкт симулятора для логування
        
        Returns:
            Оптимальний запит для поточного напрямку або None
        """
        if not self.queue:
            return None
        
        sorted_queue = sorted(self.queue, key=lambda r: r.sector)
        current_track = disk.current_track
        
        if self.last_track is not None and self.last_track == current_track:
            self.current_track_accesses += 1
            if self.current_track_accesses >= self.max_track_accesses:
                self.direction_increasing = not self.direction_increasing
                self.current_track_accesses = 0
                simulator.log(f"IO Scheduler (LOOK): changed direction to "
                            f"{'increasing' if self.direction_increasing else 'decreasing'}")
        else:
            self.current_track_accesses = 0
        
        self.last_track = current_track
        
        selected = None
        if self.direction_increasing:
            for req in sorted_queue:
                req_track = req.get_track(disk.sectors_per_track)
                if req_track >= current_track:
                    selected = req
                    break
            
            if selected is None and sorted_queue:
                self.direction_increasing = False
                self.current_track_accesses = 0
                
                seek_to_first, _ = disk.calculate_seek_time(
                    sorted_queue[0].get_track(disk.sectors_per_track))
                seek_to_last, _ = disk.calculate_seek_time(
                    sorted_queue[-1].get_track(disk.sectors_per_track))
                
                selected = sorted_queue[0] if seek_to_first <= seek_to_last else sorted_queue[-1]
                simulator.log(f"IO Scheduler (LOOK): no requests in current direction, "
                            f"changed to decreasing")
        else:
            for req in reversed(sorted_queue):
                req_track = req.get_track(disk.sectors_per_track)
                if req_track <= current_track:
                    selected = req
                    break
            
            if selected is None and sorted_queue:
                self.direction_increasing = True
                self.current_track_accesses = 0
                
                seek_to_first, _ = disk.calculate_seek_time(
                    sorted_queue[0].get_track(disk.sectors_per_track))
                seek_to_last, _ = disk.calculate_seek_time(
                    sorted_queue[-1].get_track(disk.sectors_per_track))
                
                selected = sorted_queue[0] if seek_to_first <= seek_to_last else sorted_queue[-1]
                simulator.log(f"IO Scheduler (LOOK): no requests in current direction, "
                            f"changed to increasing")
        
        if selected:
            self.queue.remove(selected)
            simulator.log(f"IO Scheduler (LOOK): selected request sector {selected.sector} "
                        f"(direction: {'increasing' if self.direction_increasing else 'decreasing'})")
        
        return selected