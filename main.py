"""
Головний модуль програми для симуляції планування введення-виведення.

Цей модуль забезпечує інтерфейс командного рядка для запуску симуляції
операційної системи з різними конфігураціями параметрів, алгоритмами
планування введення-виведення та сценаріями виконання процесів користувача.

Програма підтримує повне налаштування всіх параметрів системи через
аргументи командного рядка, включаючи характеристики жорсткого диска,
розмір буферного кешу, квант часу процесора та вибір алгоритму планування.
"""

import sys
from typing import Optional

from config import SystemConfig, parse_arguments, validate_config
from core.disk import HardDisk
from core.buffer_cache import BufferCacheLRU2Q
from schedulers.fifo import FIFOScheduler
from schedulers.look import LOOKScheduler
from schedulers.nlook import NLOOKScheduler
from simulator.simulator import Simulator
from scenarios.scenario1 import create_default_scenario
from scenarios.scenario2 import create_sequential_scenario, create_random_scenario
from scenarios.scenario3 import create_cache_test_scenario


def create_scheduler(scheduler_name: str):
    """
    Створює екземпляр планувальника введення-виведення відповідно до назви.
    
    Функція виконує фабричне створення об'єкта планувальника на основі
    текстової назви алгоритму, що дозволяє динамічно обирати реалізацію
    алгоритму планування під час виконання програми через параметри
    командного рядка без необхідності модифікації вихідного коду.
    
    Args:
        scheduler_name: Назва алгоритму планування введення-виведення, що
                       підтримується системою та визначає стратегію обробки
                       черги запитів до жорсткого диска
        
    Returns:
        Екземпляр класу планувальника, що реалізує інтерфейс IOScheduler
        та забезпечує логіку вибору наступного запиту для виконання
        
    Raises:
        ValueError: Якщо передано назву алгоритму, що не підтримується
                   системою або містить помилку у написанні назви
    """
    schedulers = {
        'fifo': FIFOScheduler,
        'look': LOOKScheduler,
        'nlook': NLOOKScheduler,
    }
    
    scheduler_class = schedulers.get(scheduler_name.lower())
    if scheduler_class is None:
        available = ', '.join(schedulers.keys())
        raise ValueError(
            f"Невідомий алгоритм планування: {scheduler_name}. "
            f"Доступні варіанти: {available}"
        )
    
    return scheduler_class()


def create_scenario(scenario_name: str, config: SystemConfig):
    """
    Створює набір процесів користувача відповідно до обраного сценарію.
    
    Функція генерує список процесів з різними послідовностями операцій
    читання та запису секторів диска залежно від обраного тестового
    сценарію. Кожен сценарій демонструє специфічні патерни звернень
    для аналізу ефективності алгоритмів планування та буферного кешу.
    
    Args:
        scenario_name: Назва тестового сценарію, що визначає характер
                      операцій процесів та патерни звернень до диска
        config: Об'єкт конфігурації системи з параметрами для генерації
               відповідної кількості процесів та налаштувань диска
        
    Returns:
        Список об'єктів Process з послідовностями операцій відповідно
        до логіки обраного сценарію для виконання симуляції системи
        
    Raises:
        ValueError: Якщо передано назву сценарію, що не реалізовано
                   в системі або містить синтаксичну помилку
    """
    scenarios = {
        'default': create_default_scenario,
        'sequential': create_sequential_scenario,
        'random': create_random_scenario,
        'cache-test': create_cache_test_scenario,
    }
    
    scenario_func = scenarios.get(scenario_name.lower())
    if scenario_func is None:
        available = ', '.join(scenarios.keys())
        raise ValueError(
            f"Невідомий сценарій: {scenario_name}. "
            f"Доступні варіанти: {available}"
        )
    
    return scenario_func(config)

def print_configuration(config: SystemConfig):
    """
    Виводить поточну конфігурацію всіх параметрів системи симуляції.
    
    Функція відображає детальну інформацію про налаштування симуляції,
    включаючи вибраний алгоритм планування, параметри жорсткого диска,
    конфігурацію буферного кешу та інші системні параметри. Це забезпечує
    повну документацію умов виконання експерименту для аналізу результатів.
    
    Args:
        config: Об'єкт конфігурації з усіма параметрами системи для виведення
               у структурованому форматі для зручності читання та аналізу
    """
    print("Конфігурація системи:")
    print(f"  Алгоритм планування: {config.scheduler_name.upper()}")
    print(f"  Кількість процесів: {config.num_processes}")
    print(f"  Сценарій виконання: {config.scenario_name}")
    print(f"  Квант часу: {config.quantum} мс")
    print()
    print("Параметри жорсткого диска:")
    print(f"  Кількість доріжок: {config.num_tracks}")
    print(f"  Секторів на доріжці: {config.sectors_per_track}")
    print(f"  Швидкість обертання: {config.rpm} RPM")
    print(f"  Час пошуку доріжки: {config.seek_time_per_track} мс")
    print()
    print("Параметри буферного кешу:")
    print(f"  Кількість буферів: {config.total_buffers}")
    print(f"  Максимальний правий сегмент: {config.max_right_segment}")
    print()
    if config.output_file:
        print(f"Результати будуть збережені у: {config.output_file}")
        print()
    print("-" * 80)
    print()


def redirect_output(filename: Optional[str]):
    """
    Перенаправляє стандартний вивід програми у файл при необхідності.
    
    Функція забезпечує можливість збереження результатів симуляції у файл
    для подальшого аналізу та порівняння різних конфігурацій. У разі
    відсутності імені файлу або помилки його відкриття використовується
    стандартний вивід для відображення результатів у терміналі.
    
    Args:
        filename: Шлях до файлу для збереження виводу програми або значення
                 None для використання стандартного виводу в термінал
        
    Returns:
        Відкритий файловий об'єкт для запису результатів або sys.stdout
        для виведення в термінал у разі відсутності файлу або помилки
    """
    if filename:
        try:
            return open(filename, 'w', encoding='utf-8')
        except IOError as e:
            print(f"Помилка відкриття файлу {filename}: {e}", file=sys.stderr)
            print("Використовується стандартний вивід.", file=sys.stderr)
            return sys.stdout
    return sys.stdout


def main():
    """
    Головна функція програми для керування виконанням симуляції системи.
    
    Функція виконує повний цикл роботи програми, включаючи парсинг аргументів
    командного рядка, валідацію конфігурації, створення компонентів системи,
    запуск симуляції та обробку помилок. Забезпечує коректне завершення
    програми з відповідним кодом виходу залежно від результату виконання.
    
    Послідовність виконання включає наступні етапи: отримання конфігурації
    з аргументів командного рядка, перевірка коректності параметрів,
    перенаправлення виводу при необхідності, створення моделі жорсткого
    диска та буферного кешу, ініціалізація планувальника введення-виведення,
    генерація процесів відповідно до сценарію, створення симулятора та
    запуск повного циклу моделювання роботи операційної системи.
    
    Returns:
        Код завершення програми, де нуль означає успішне виконання симуляції,
        один вказує на помилку конфігурації або виконання, а сто тридцять
        сигналізує про переривання програми користувачем через клавіатуру
    """
    try:
        config = parse_arguments(sys.argv[1:])
        validate_config(config)
        
        original_stdout = sys.stdout
        output_file = redirect_output(config.output_file)
        
        try:
            sys.stdout = output_file
            
            print_configuration(config)
            
            disk = HardDisk(
                num_tracks=config.num_tracks,
                sectors_per_track=config.sectors_per_track,
                seek_time_per_track=config.seek_time_per_track,
                seek_time_to_edge=config.seek_time_to_edge,
                rpm=config.rpm
            )
            
            buffer_cache = BufferCacheLRU2Q(
                total_buffers=config.total_buffers,
                max_right_segment=config.max_right_segment
            )
            
            io_scheduler = create_scheduler(config.scheduler_name)
            
            processes = create_scenario(config.scenario_name, config)
            
            simulator = Simulator(
                disk=disk,
                buffer_cache=buffer_cache,
                io_scheduler=io_scheduler,
                processes=processes,
                quantum=config.quantum,
                syscall_time=config.syscall_time,
                interrupt_time=config.interrupt_time,
                compute_time=config.compute_time,
                verbose=config.verbose
            )
            
            simulator.run()
            
        finally:
            if output_file != sys.stdout:
                output_file.close()
            sys.stdout = original_stdout
            
            if config.output_file:
                print(f"\nРезультати збережено у файл: {config.output_file}")
        
        return 0
        
    except ValueError as e:
        print(f"Помилка конфігурації: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n\nСимуляцію перервано користувачем.", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Критична помилка: {e}", file=sys.stderr)
        if 'config' in locals() and hasattr(locals()['config'], 'verbose') and locals()['config'].verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)