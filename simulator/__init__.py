"""
Пакет компонентів симулятора операційної системи.

Містить головний модуль симуляції на основі дискретних подій
та допоміжний модуль збору статистики виконання.
"""

from simulator.simulator import Simulator
from simulator.statistics import Statistics

__all__ = ['Simulator', 'Statistics']

