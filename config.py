"""
Модуль конфігурації системи.

Цей модуль визначає параметри системи, які можуть бути налаштовані через
аргументи командного рядка. Забезпечує парсинг, валідацію та збереження
конфігурації для використання в інших модулях програми.

"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class SystemConfig:
    """
    Клас конфігурації системи, що містить усі параметри для симуляції.
    
    Атрибути для параметрів диска:
        num_tracks: Кількість доріжок на жорсткому диску
        sectors_per_track: Кількість секторів на одній доріжці
        seek_time_per_track: Час переміщення головки на одну доріжку (мс)
        seek_time_to_edge: Час переміщення до крайньої доріжки (мс)
        rpm: Швидкість обертання диска (обертів за хвилину)
    
    Атрибути для параметрів буферного кешу:
        total_buffers: Загальна кількість буферів
        max_right_segment: Максимальний розмір правого сегмента для LRU 2Q
    
    Атрибути для параметрів планування:
        quantum: Квант часу для виконання процесу (мс)
        syscall_time: Час виконання системного виклику (мс)
        interrupt_time: Час обробки апаратного переривання (мс)
        compute_time: Час обробки даних процесом (мс)
    
    Атрибути для конфігурації симуляції:
        scheduler_name: Назва алгоритму планування введення-виведення
        num_processes: Кількість процесів користувача
        scenario_name: Назва сценарію для виконання
        output_file: Шлях до файлу для збереження результатів
        verbose: Прапорець детального виведення
    """
    
    num_tracks: int = 10000
    sectors_per_track: int = 500
    seek_time_per_track: float = 0.5
    seek_time_to_edge: float = 10.0
    rpm: int = 7500
    
    total_buffers: int = 10
    max_right_segment: int = 5
    
    quantum: float = 20.0
    syscall_time: float = 0.15
    interrupt_time: float = 0.05
    compute_time: float = 7.0
    
    scheduler_name: str = 'fifo'
    num_processes: int = 2
    scenario_name: str = 'default'
    output_file: Optional[str] = None
    verbose: bool = False


def parse_arguments(args: List[str]) -> SystemConfig:
    """
    Парсить аргументи командного рядка та створює конфігурацію системи.
    
    Args:
        args: Список аргументів командного рядка (sys.argv[1:])
    
    Returns:
        SystemConfig: Об'єкт конфігурації з параметрами системи
    
    Raises:
        ValueError: Якщо передано некоректні аргументи або значення
    """
    config = SystemConfig()
    
    i = 0
    while i < len(args):
        arg = args[i]
        
        if arg in ('-h', '--help'):
            print_help()
            raise SystemExit(0)
        
        elif arg == '--scheduler':
            if i + 1 >= len(args):
                raise ValueError("Аргумент --scheduler потребує значення")
            config.scheduler_name = args[i + 1]
            i += 2
        
        elif arg == '--processes':
            if i + 1 >= len(args):
                raise ValueError("Аргумент --processes потребує значення")
            try:
                config.num_processes = int(args[i + 1])
            except ValueError:
                raise ValueError(f"Некоректне значення для --processes: {args[i + 1]}")
            i += 2
        
        elif arg == '--quantum':
            if i + 1 >= len(args):
                raise ValueError("Аргумент --quantum потребує значення")
            try:
                config.quantum = float(args[i + 1])
            except ValueError:
                raise ValueError(f"Некоректне значення для --quantum: {args[i + 1]}")
            i += 2
        
        elif arg == '--buffers':
            if i + 1 >= len(args):
                raise ValueError("Аргумент --buffers потребує значення")
            try:
                config.total_buffers = int(args[i + 1])
            except ValueError:
                raise ValueError(f"Некоректне значення для --buffers: {args[i + 1]}")
            i += 2
        
        elif arg == '--tracks':
            if i + 1 >= len(args):
                raise ValueError("Аргумент --tracks потребує значення")
            try:
                config.num_tracks = int(args[i + 1])
            except ValueError:
                raise ValueError(f"Некоректне значення для --tracks: {args[i + 1]}")
            i += 2
        
        elif arg == '--sectors-per-track':
            if i + 1 >= len(args):
                raise ValueError("Аргумент --sectors-per-track потребує значення")
            try:
                config.sectors_per_track = int(args[i + 1])
            except ValueError:
                raise ValueError(f"Некоректне значення для --sectors-per-track: {args[i + 1]}")
            i += 2
        
        elif arg == '--rpm':
            if i + 1 >= len(args):
                raise ValueError("Аргумент --rpm потребує значення")
            try:
                config.rpm = int(args[i + 1])
            except ValueError:
                raise ValueError(f"Некоректне значення для --rpm: {args[i + 1]}")
            i += 2
        
        elif arg == '--scenario':
            if i + 1 >= len(args):
                raise ValueError("Аргумент --scenario потребує значення")
            config.scenario_name = args[i + 1]
            i += 2
        
        elif arg == '--output':
            if i + 1 >= len(args):
                raise ValueError("Аргумент --output потребує значення")
            config.output_file = args[i + 1]
            i += 2
        
        elif arg == '--verbose':
            config.verbose = True
            i += 1
        
        else:
            raise ValueError(f"Невідомий аргумент: {arg}. Використовуйте --help для довідки")
    
    return config


def validate_config(config: SystemConfig) -> None:
    """
    Перевіряє коректність параметрів конфігурації.
    
    Args:
        config: Конфігурація для валідації
    
    Raises:
        ValueError: Якщо знайдено некоректні значення параметрів
    """
    if config.num_tracks <= 0:
        raise ValueError("Кількість доріжок повинна бути додатною")
    
    if config.sectors_per_track <= 0:
        raise ValueError("Кількість секторів на доріжці повинна бути додатною")
    
    if config.seek_time_per_track < 0:
        raise ValueError("Час пошуку доріжки не може бути від'ємним")
    
    if config.seek_time_to_edge < 0:
        raise ValueError("Час переміщення до краю не може бути від'ємним")
    
    if config.rpm <= 0:
        raise ValueError("Швидкість обертання диска повинна бути додатною")
    
    if config.total_buffers <= 0:
        raise ValueError("Кількість буферів повинна бути додатною")
    
    if config.max_right_segment >= config.total_buffers:
        raise ValueError(
            "Максимальний розмір правого сегмента повинен бути меншим "
            "за загальну кількість буферів"
        )
    
    if config.quantum <= 0:
        raise ValueError("Квант часу повинен бути додатним")
    
    if config.syscall_time < 0:
        raise ValueError("Час системного виклику не може бути від'ємним")
    
    if config.interrupt_time < 0:
        raise ValueError("Час обробки переривання не може бути від'ємним")
    
    if config.compute_time < 0:
        raise ValueError("Час обробки даних не може бути від'ємним")
    
    if config.num_processes <= 0:
        raise ValueError("Кількість процесів повинна бути додатною")
    
    valid_schedulers = ['fifo', 'look', 'nlook', 'flook']
    if config.scheduler_name.lower() not in valid_schedulers:
        raise ValueError(
            f"Невідомий алгоритм планування: {config.scheduler_name}. "
            f"Доступні варіанти: {', '.join(valid_schedulers)}"
        )


def print_help():
    """Виводить довідкову інформацію про використання програми."""
    help_text = """
Використання: python main.py [ОПЦІЇ]

Симуляція алгоритмів планування введення-виведення для жорсткого диска.

Обов'язкові аргументи:
  --scheduler NAME           Алгоритм планування I/O (fifo, look, nlook, flook)

Необов'язкові аргументи:
  --processes N              Кількість процесів користувача (за замовчуванням: 2)
  --quantum TIME             Квант часу в мілісекундах (за замовчуванням: 20.0)
  --buffers N                Кількість буферів у кеші (за замовчуванням: 10)
  --tracks N                 Кількість доріжок на диску (за замовчуванням: 10000)
  --sectors-per-track N      Секторів на доріжці (за замовчуванням: 500)
  --rpm N                    Швидкість обертання диска (за замовчуванням: 7500)
  --scenario NAME            Сценарій виконання (за замовчуванням: default)
  --output FILE              Файл для збереження результатів
  --verbose                  Детальний вивід інформації
  -h, --help                 Вивести цю довідку

Доступні алгоритми планування:
  fifo                       First In First Out - черга за порядком надходження
  look                       LOOK - сортування з напрямком руху головки
  nlook                      N-LOOK - кілька черг з обмеженою довжиною
  flook                      F-LOOK - дві черги (активна та очікувальна)

Доступні сценарії:
  default                    Стандартний сценарій з різними зверненнями
  sequential                 Послідовні звернення до секторів
  random                     Випадкові звернення по всьому диску
  cache-test                 Тест ефективності буферного кешу

Приклади використання:
  python main.py --scheduler fifo
  python main.py --scheduler look --processes 3 --verbose
  python main.py --scheduler nlook --scenario random --output results.txt
  python main.py --scheduler flook --buffers 15 --rpm 5400
    """
    print(help_text)