"""
Пакет основних компонентів системи.

Містить реалізації моделей жорсткого диска, буферного кешу,
процесів та типів подій для симуляції.
"""

from core.disk import HardDisk
from core.buffer_cache import BufferCacheLRU2Q
from core.process import Process
from core.events import RequestType, EventType, IORequest, Event, Buffer

__all__ = [
    'HardDisk',
    'BufferCacheLRU2Q',
    'Process',
    'RequestType',
    'EventType',
    'IORequest',
    'Event',
    'Buffer',
]
