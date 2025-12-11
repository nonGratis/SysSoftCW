# Алгоритми планування введення-виведення для жорсткого диска

Курсова робота з дисципліни "Системне програмне забезпечення"

## Опис проекту

Проект реалізує симуляцію роботи операційної системи з жорстким диском, включаючи:

- Алгоритм управління буферним кешем (LRU з двома сегментами)
- Три алгоритми планування введення-виведення: FIFO, LOOK, NLOOK
- Моделювання процесів користувача з квантуванням часу
- Детальне логування всіх операцій системи

## Встановлення

### Вимоги
- Python 3.8 або новіший

### Клонування репозиторію
```bash
git clone ??
cd disk-io-scheduler
```

### Встановлення залежностей
```bash
pip install -r requirements.txt
```

## Використання

### Базовий запуск з алгоритмом FIFO
```bash
python main.py --scheduler fifo
```

### Запуск з алгоритмом LOOK
```bash
python main.py --scheduler look --verbose
```

### Збереження результатів у файл
```bash
python main.py --scheduler nlook --output output/nlook_results.txt
```

### Налаштування параметрів системи
```bash
python main.py --scheduler nlook --processes 3 --quantum 30 --buffers 15 --rpm 5400
```

## Параметри командного рядка

**Обов'язкові параметри:**
- `--scheduler` - алгоритм планування: `fifo`, `look`, `nlook`

**Необов'язкові параметри:**
- `--processes N` - кількість процесів (за замовчуванням: 2)
- `--quantum TIME` - квант часу в мілісекундах (за замовчуванням: 20.0)
- `--buffers N` - кількість буферів у кеші (за замовчуванням: 10)
- `--tracks N` - кількість доріжок на диску (за замовчуванням: 10000)
- `--sectors-per-track N` - секторів на доріжці (за замовчуванням: 500)
- `--rpm N` - швидкість обертання диска (за замовчуванням: 7500)
- `--scenario NAME` - сценарій виконання (за замовчуванням: default)
- `--output FILE` - файл для збереження результатів
- `--verbose` - детальний вивід

## Сценарії тестування

### default
Стандартний сценарій з двома процесами та змішаними зверненнями до секторів.

### sequential
Процеси звертаються до послідовних секторів, що демонструє ефективність алгоритмів LOOK/NLOOK.

### random
Випадкові звернення до секторів по всьому диску, найбільш складний випадок для планувальників.

### cache-test
Сценарій з повторними зверненнями до одних і тих же секторів для демонстрації роботи буферного кешу.

## Приклади експериментів

### Порівняння алгоритмів планування
```bash
python main.py --scheduler fifo --scenario random --output output/fifo.txt
python main.py --scheduler look --scenario random --output output/look.txt
python main.py --scheduler nlook --scenario random --output output/nlook.txt
```

### Аналіз впливу параметрів диска
```bash
# Швидкий диск (15000 RPM)
python main.py --scheduler look --rpm 15000 --output output/fast.txt

# Стандартний диск (7500 RPM)
python main.py --scheduler look --rpm 7500 --output output/standard.txt

# Повільний диск (5400 RPM)
python main.py --scheduler look --rpm 5400 --output output/slow.txt
```

### Тестування буферного кешу
```bash
# Малий кеш (5 буферів)
python main.py --buffers 5 --scenario cache-test --output output/small_cache.txt

# Середній кеш (10 буферів)
python main.py --buffers 10 --scenario cache-test --output output/medium_cache.txt

# Великий кеш (20 буферів)
python main.py --buffers 20 --scenario cache-test --output output/large_cache.txt
```

## Структура проекту

```
disk-io-scheduler/
├── main.py                 # Точка входу
├── config.py              # Конфігурація
├── core/                  # Основні компоненти
│   ├── disk.py           # Модель диска
│   ├── buffer_cache.py   # Буферний кеш
│   ├── process.py        # Процеси
│   └── events.py         # Події системи
├── schedulers/            # Алгоритми планування
│   ├── fifo.py
│   ├── look.py
│   └── nlook.py
├── simulator/             # Симулятор
│   ├── simulator.py
│   └── statistics.py
└── scenarios/             # Тестові сценарії
    ├── scenario1.py
    ├── scenario2.py
    └── scenario3.py
```

## Результати симуляції

Програма виводить детальний лог виконання системи, що включає:

- Час кожної події в мілісекундах
- Системні виклики процесів (read/write)
- Стан буферного кешу (hit/miss)
- Операції планувальника I/O
- Переміщення головки диска
- Обробку апаратних переривань
- Статистику виконання

Приклад виводу:
```
Time:     0.00 ms | Process 1: started (quantum: 20.0 ms)
Time:     0.00 ms | Buffer cache: MISS sector 1250
Time:     0.15 ms | IO Scheduler (LOOK): added request READ sector 1250
Time:     0.15 ms | Disk: seeking to track 2 (direct 2 tracks, 1.00 ms)
Time:     1.15 ms | Disk: rotational latency 4.00 ms
```

