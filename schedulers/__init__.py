"""
Пакет алгоритмів планування введення-виведення.

Містить реалізації чотирьох алгоритмів планування запитів до жорсткого диска:
FIFO, LOOK, NLOOK.
"""

from schedulers.base import IOScheduler
from schedulers.fifo import FIFOScheduler
from schedulers.look import LOOKScheduler
from schedulers.nlook import NLOOKScheduler

__all__ = [
    'IOScheduler',
    'FIFOScheduler',
    'LOOKScheduler',
    'NLOOKScheduler',
]
