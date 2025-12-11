
"""
Модуль збору статистики виконання симуляції.

Збирає та аналізує дані про роботу системи для оцінки ефективності
алгоритмів планування та буферного кешу.


"""


class Statistics:
    """
    Клас для збору та аналізу статистики виконання симуляції.
    
    Атрибути:
        total_disk_seeks: Загальна кількість переміщень головки диска
        total_disk_time: Сумарний час операцій диска (мілісекунди)
        cache_hits: Кількість влучень у буферний кеш
        cache_misses: Кількість промахів буферного кешу
        finished_processes: Множина ідентифікаторів завершених процесів
    """
    
    def __init__(self):
        """Ініціалізує об'єкт статистики з нульовими значеннями."""
        self.total_disk_seeks = 0
        self.total_disk_time = 0.0
        self.cache_hits = 0
        self.cache_misses = 0
        self.finished_processes = set()
    
    def record_disk_seek(self, seek_time: float):
        """
        Реєструє операцію пошуку доріжки диска.
        
        Args:
            seek_time: Час виконання пошуку (мілісекунди)
        """
        self.total_disk_seeks += 1
        self.total_disk_time += seek_time
    
    def record_cache_hit(self):
        """Реєструє влучення у буферний кеш."""
        self.cache_hits += 1
    
    def record_cache_miss(self):
        """Реєструє промах буферного кешу."""
        self.cache_misses += 1
    
    def process_finished(self, pid: int):
        """
        Реєструє завершення процесу.
        
        Args:
            pid: Ідентифікатор завершеного процесу
        """
        self.finished_processes.add(pid)
    
    def get_cache_hit_rate(self) -> float:
        """
        Обчислює відсоток влучень у буферний кеш.
        
        Returns:
            Відсоток влучень від загальної кількості звернень
        """
        total_accesses = self.cache_hits + self.cache_misses
        if total_accesses == 0:
            return 0.0
        return (self.cache_hits / total_accesses) * 100
    
    def print_statistics(self, simulator):
        """
        Виводить детальну статистику виконання симуляції.
        
        Args:
            simulator: Об'єкт симулятора для доступу до його параметрів
        """
        print()
        print("СТАТИСТИКА ВИКОНАННЯ:")
        print(f"  Загальний час симуляції: {simulator.current_time:.2f} мс")
        print(f"  Кількість переміщень головки: {self.total_disk_seeks}")
        print(f"  Сумарний час пошуку доріжок: {self.total_disk_time:.2f} мс")
        
        if self.total_disk_seeks > 0:
            avg_seek = self.total_disk_time / self.total_disk_seeks
            print(f"  Середній час пошуку: {avg_seek:.2f} мс")
        
        print()
        print("СТАТИСТИКА БУФЕРНОГО КЕШУ:")
        print(f"  Влучення: {self.cache_hits}")
        print(f"  Промахи: {self.cache_misses}")
        print(f"  Відсоток влучень: {self.get_cache_hit_rate():.2f}%")
        print(f"  {simulator.buffer_cache.get_stats()}")
        
        print()
        print("СТАТИСТИКА ПРОЦЕСІВ:")
        total = len(simulator.processes)
        finished = len(self.finished_processes)
        print(f"  Загальна кількість процесів: {total}")
        print(f"  Завершено процесів: {finished}")
        
        for process in simulator.processes:
            completed = process.current_index
            total_ops = len(process.sector_sequence)
            status = "FINISHED" if process.is_finished() else process.state
            print(f"  Process {process.pid}: {completed}/{total_ops} операцій, стан: {status}")