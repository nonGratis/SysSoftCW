
"""
Пакет сценаріїв для тестування системи.

Містить різні конфігурації процесів та патернів звернень
для демонстрації роботи алгоритмів планування.
"""

from scenarios.scenario1 import create_default_scenario
from scenarios.scenario2 import create_sequential_scenario, create_random_scenario
from scenarios.scenario3 import create_cache_test_scenario

__all__ = [
    'create_default_scenario',
    'create_sequential_scenario',
    'create_random_scenario',
    'create_cache_test_scenario',
]
