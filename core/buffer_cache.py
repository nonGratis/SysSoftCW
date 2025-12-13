"""
Модуль реалізації буферного кешу з алгоритмом LRU із двома сегментами.

Реалізує управління буферним кешем операційної системи з використанням
модифікованого алгоритму LRU (Least Recently Used), що розділяє кеш на два
сегменти для підвищення ефективності роботи з різними патернами звернень.


"""

from collections import deque
from typing import Optional, Tuple

from core.events import Buffer


class BufferCacheLRU2Q:
    """
    Буферний кеш із алгоритмом LRU з двома сегментами.
    
    Кеш складається з лівого та правого сегментів. Лівий сегмент містить буфери,
    до яких було зроблено лише одне звернення, тоді як правий сегмент містить
    буфери з повторними зверненнями. Це дозволяє уникнути витіснення часто
    використовуваних буферів одноразовими зверненнями.
    
    Атрибути:
        total_buffers: Загальна кількість буферів у системі
        max_right_segment: Максимальний розмір правого сегмента
        left_segment: Лівий сегмент (deque для ефективних операцій)
        right_segment: Правий сегмент (deque для ефективних операцій)
        sector_to_buffer: Відображення номера сектора на об'єкт Buffer
        free_buffers: Список номерів вільних буферів
    """
    
    def __init__(self, total_buffers: int, max_right_segment: int):
        """
        Ініціалізує буферний кеш із заданими параметрами.
        
        Args:
            total_buffers: Загальна кількість буферів у кеші
            max_right_segment: Максимальний розмір правого сегмента
        """
        self.total_buffers = total_buffers
        self.max_right_segment = max_right_segment
        
        self.left_segment = deque()
        self.right_segment = deque()
        
        self.sector_to_buffer = {}
    
    def find_buffer(self, sector: int) -> Optional[Buffer]:
        """
        Виконує пошук буфера для заданого сектора у кеші.
        
        Args:
            sector: Номер сектора для пошуку
        
        Returns:
            Об'єкт Buffer якщо сектор знайдено у кеші, інакше None
        """
        return self.sector_to_buffer.get(sector)
    
    def access_buffer(self, sector: int, simulator) -> Tuple[Buffer, bool]:
        """
        Обробляє звернення до буфера із заданим сектором.
        
        Метод реалізує логіку алгоритму LRU з двома сегментами. Якщо буфер
        знайдено у кеші, він переміщується на початок правого сегмента.
        Якщо буфер не знайдено, виділяється новий буфер або витісняється
        існуючий, після чого додається на початок лівого сегмента.
        
        Args:
            sector: Номер сектора для звернення
            simulator: Об'єкт симулятора для логування подій
        
        Returns:
            Кортеж із об'єкта Buffer та прапорця промаху кешу (True при промаху)
        """
        buffer = self.find_buffer(sector)
        
        if buffer is not None:
            simulator.log(f"Buffer cache: HIT sector {sector}")
            
            if buffer in self.left_segment:
                self.left_segment.remove(buffer)
            elif buffer in self.right_segment:
                self.right_segment.remove(buffer)
            
            self._add_to_right_segment(buffer, simulator)
            
            return buffer, False
        else:
            simulator.log(f"Buffer cache: MISS sector {sector}")
            
            # Перевіряємо чи є вільне місце
            current_buffers = len(self.left_segment) + len(self.right_segment)
            
            if current_buffers < self.total_buffers:
                # Є вільне місце - створюємо новий буфер
                simulator.log(f"Buffer cache: allocated new buffer")
                buffer = Buffer(sector)
            else:
                # Немає місця - витісняємо з кінця лівого сегмента
                if not self.left_segment:
                    # Якщо лівий сегмент порожній, витісняємо з правого
                    evicted = self.right_segment.pop()
                    simulator.log(f"Buffer cache: evicted sector {evicted.sector} from right segment")
                else:
                    evicted = self.left_segment.pop()
                    simulator.log(f"Buffer cache: evicted sector {evicted.sector} from left segment")
                
                # Видаляємо зі словника
                del self.sector_to_buffer[evicted.sector]
                
                # Створюємо новий буфер
                buffer = Buffer(sector)
            
            # Додаємо буфер до словника та на початок лівого сегмента
            self.sector_to_buffer[sector] = buffer
            self.left_segment.appendleft(buffer)
            simulator.log(f"Buffer cache: added sector {sector} to left segment start")
            
            return buffer, True
    
    def _add_to_right_segment(self, buffer: Buffer, simulator):
        """
        Додає буфер на початок правого сегмента з обробкою переповнення.
        
        Якщо правий сегмент досяг максимального розміру, останній буфер
        переміщується на початок лівого сегмента перед додаванням нового.
        
        Args:
            buffer: Буфер для додавання до правого сегмента
            simulator: Об'єкт симулятора для логування
        """
        if len(self.right_segment) >= self.max_right_segment:
            moved = self.right_segment.pop()
            self.left_segment.appendleft(moved)
            simulator.log(f"Buffer cache: moved sector {moved.sector} "
                         f"from right to left segment")
        
        self.right_segment.appendleft(buffer)
        simulator.log(f"Buffer cache: moved sector {buffer.sector} "
                     f"to right segment start")
    
    def get_stats(self) -> str:
        """
        Формує рядок із статистикою поточного стану буферного кешу.
        
        Returns:
            Текстовий опис розподілу буферів по сегментах
        """
        return (f"Left segment: {len(self.left_segment)} buffers, "
                f"Right segment: {len(self.right_segment)} buffers, "
                f"Free: {free} buffers")