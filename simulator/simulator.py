
"""
Головний модуль системи дискретного подійного моделювання.

Реалізує координацію роботи всіх компонентів системи: процесів, планувальника
введення-виведення, буферного кешу та жорсткого диска.


"""

import heapq
from typing import List
from core.disk import HardDisk
from core.buffer_cache import BufferCacheLRU2Q
from core.disk import HardDisk
from core.events import Event, EventType, IORequest
from core.process import Process
from core.events import Event, EventType, IORequest, RequestType
from schedulers.base import IOScheduler
from simulator.statistics import Statistics


class Simulator:
    """
    Система дискретного подійного моделювання операційної системи.
    
    Координує роботу процесів користувача, буферного кешу, планувальника
    введення-виведення та жорсткого диска. Моделює квантування часу для
    процесів та обробку апаратних переривань.
    
    Атрибути:
        disk: Модель жорсткого диска
        buffer_cache: Буферний кеш з алгоритмом LRU 2Q
        io_scheduler: Планувальник запитів введення-виведення
        processes: Список процесів користувача
        quantum: Квант часу для виконання процесу (мілісекунди)
        syscall_time: Час виконання системного виклику (мілісекунди)
        interrupt_time: Час обробки апаратного переривання (мілісекунди)
        compute_time: Час обробки даних процесом (мілісекунди)
        verbose: Прапорець детального виведення інформації
        current_time: Поточний час симуляції (мілісекунди)
        event_queue: Черга подій з пріоритетами
        current_process: Поточний активний процес
        current_io_request: Поточний запит, що виконується диском
        statistics: Об'єкт для збору статистики виконання
    """
    
    def __init__(self, disk: HardDisk, buffer_cache: BufferCacheLRU2Q,
                 io_scheduler: IOScheduler, processes: List[Process],
                 quantum: float, syscall_time: float, interrupt_time: float,
                 compute_time: float, verbose: bool = False):
        """
        Ініціалізує симулятор з компонентами системи.
        
        Args:
            disk: Модель жорсткого диска
            buffer_cache: Буферний кеш
            io_scheduler: Планувальник введення-виведення
            processes: Список процесів для виконання
            quantum: Квант часу для процесів
            syscall_time: Час системного виклику
            interrupt_time: Час обробки переривання
            compute_time: Час обробки даних
            verbose: Режим детального виведення
        """
        self.disk = disk
        self.buffer_cache = buffer_cache
        self.io_scheduler = io_scheduler
        self.processes = processes
        
        self.quantum = quantum
        self.syscall_time = syscall_time
        self.interrupt_time = interrupt_time
        self.compute_time = compute_time
        self.verbose = verbose
        
        self.current_time = 0.0
        self.event_queue = []
        self.current_process = None
        self.current_io_request = None
        
        self.statistics = Statistics()
    
    def log(self, message: str):
        """
        Виводить повідомлення з поточним часом симуляції.
        
        Args:
            message: Текст повідомлення для виведення
        """
        print(f"Time: {self.current_time:8.3f} ms | {message}")
    
    def schedule_event(self, delay: float, event_type: EventType, data: dict):
        """
        Додає нову подію до черги подій.
        
        Args:
            delay: Затримка до виникнення події (мілісекунди)
            event_type: Тип події
            data: Додаткові дані для події
        """
        event = Event(self.current_time + delay, event_type, data)
        heapq.heappush(self.event_queue, event)
    
    def run(self):
        """
        Запускає головний цикл симуляції.
        
        Виконує послідовну обробку подій із черги до її повного спорожнення.
        Після завершення виводить статистику виконання.
        """        
        if self.processes:
            self.schedule_event(0, EventType.PROCESS_START, {'process': self.processes[0]})
        
        while self.event_queue:
            event = heapq.heappop(self.event_queue)
            self.current_time = event.time
            
            # Обробка події
            if event.event_type == EventType.PROCESS_START:
                self.handle_process_start(event.data)
            elif event.event_type == EventType.SYSCALL_START:
                self.handle_syscall_start(event.data)
            elif event.event_type == EventType.SYSCALL_END:
                self.handle_syscall_end(event.data)
            elif event.event_type == EventType.DISK_SEEK_END:
                self.handle_disk_seek_end(event.data)
            elif event.event_type == EventType.DISK_ROTATION_END:
                self.handle_disk_rotation_end(event.data)
            elif event.event_type == EventType.DISK_TRANSFER_END:
                self.handle_disk_transfer_end(event.data)
            elif event.event_type == EventType.INTERRUPT_START:
                self.handle_interrupt_start(event.data)
            elif event.event_type == EventType.INTERRUPT_END:
                self.handle_interrupt_end(event.data)
            elif event.event_type == EventType.PROCESS_COMPUTE:
                self.handle_process_compute(event.data)
            
            # Перевірка завершення всіх процесів
            if len(self.statistics.finished_processes) == len(self.processes):
                self.log("Всі процеси завершені")
                break
        
        # Вивід статистики після завершення
        self.statistics.print_statistics(self)
        
    def handle_process_start(self, data: dict):
        """Обробляє початок виконання процесу."""
        process = data['process']
        self.log(f"Process {process.pid}: started (quantum: {self.quantum} ms)")
        
        process.state = "RUNNING"
        process.quantum_remaining = self.quantum
        self.current_process = process
        
        req = process.get_next_request()
        if req:
            req_type, sector = req
            self.log(f"Process {process.pid}: next operation {req_type.value} sector {sector}")
            self.schedule_event(0, EventType.SYSCALL_START, {
                'process': process, 'req_type': req_type, 'sector': sector
            })
        else:
            process.state = "FINISHED"
            self.log(f"Process {process.pid}: FINISHED")
            self.statistics.process_finished(process.pid)
            self.schedule_next_process()
    
    def handle_syscall_start(self, data: dict):
        """Обробляє початок системного виклику."""
        process = data['process']
        req_type = data['req_type']
        sector = data['sector']
        
        self.log(f"Process {process.pid}: syscall {req_type.value}(sector={sector}) started")
        
        process.quantum_remaining -= self.syscall_time
        buffer, cache_miss = self.buffer_cache.access_buffer(sector, self)
        
        if cache_miss:
            self.statistics.record_cache_miss()
        else:
            self.statistics.record_cache_hit()
        
        self.schedule_event(self.syscall_time, EventType.SYSCALL_END, {
            'process': process, 'cache_miss': cache_miss, 'req_type': req_type, 'sector': sector
        })
    
    def handle_syscall_end(self, data: dict):
        """Обробляє завершення системного виклику."""
        process = data['process']
        cache_miss = data['cache_miss']
        req_type = data['req_type']
        sector = data['sector']
        
        if cache_miss:
            self.log(f"Process {process.pid}: syscall ended, need disk I/O")
            process.state = "BLOCKED"
            
            io_request = IORequest(sector, req_type, process.pid, self.current_time)
            self.io_scheduler.add_request(io_request, self)
            
            if self.current_io_request is None:
                self.start_disk_operation()
            
            self.schedule_next_process()
        else:
            self.log(f"Process {process.pid}: syscall ended, data in cache")
            process.advance()
            self.schedule_event(self.compute_time, EventType.PROCESS_COMPUTE, {'process': process})
    
    def start_disk_operation(self):
        """Ініціює виконання операції введення-виведення на диску."""
        if self.current_io_request is not None:
            return
        
        request = self.io_scheduler.get_next_request(self.disk, self)
        if request is None:
            return
        
        self.current_io_request = request
        target_track = request.get_track(self.disk.sectors_per_track)
        
        seek_time, seek_desc = self.disk.calculate_seek_time(target_track)
        self.statistics.record_disk_seek(seek_time)
        
        if seek_time > 0:
            self.log(f"Disk: seeking to track {target_track} ({seek_desc}, {seek_time:.2f} ms)")
            self.schedule_event(seek_time, EventType.DISK_SEEK_END, {})
        else:
            self.log(f"Disk: already at track {target_track}")
            self.schedule_event(0, EventType.DISK_SEEK_END, {})
    
    def handle_disk_seek_end(self, data: dict):
        """Обробляє завершення пошуку доріжки."""
        target_track = self.current_io_request.get_track(self.disk.sectors_per_track)
        self.disk.move_head_to(target_track)
        
        self.log(f"Disk: rotational latency {self.disk.avg_rotational_latency:.2f} ms")
        self.schedule_event(self.disk.avg_rotational_latency, EventType.DISK_ROTATION_END, {})
    
    def handle_disk_rotation_end(self, data: dict):
        """Обробляє завершення обертання диска."""
        self.log(f"Disk: transferring sector {self.current_io_request.sector} "
                f"({self.disk.sector_transfer_time:.2f} ms)")
        self.schedule_event(self.disk.sector_transfer_time, EventType.DISK_TRANSFER_END, {})
    
    def handle_disk_transfer_end(self, data: dict):
        """Обробляє завершення передачі даних."""
        self.log(f"Disk: sector {self.current_io_request.sector} transfer complete")
        self.schedule_event(0, EventType.INTERRUPT_START, {})
    
    def handle_interrupt_start(self, data: dict):
        """Обробляє початок апаратного переривання."""
        self.log(f"Interrupt: disk I/O complete for sector {self.current_io_request.sector}")
        
        if self.current_process:
            self.current_process.quantum_remaining -= self.interrupt_time
        
        blocked_pid = self.current_io_request.process_id
        blocked_process = next((p for p in self.processes if p.pid == blocked_pid), None)
        
        if blocked_process is None:
            self.log(f"ERROR: Process {blocked_pid} not found!")
            return
        
        self.schedule_event(self.interrupt_time, EventType.INTERRUPT_END, {
            'blocked_process': blocked_process
        })
    
    def handle_interrupt_end(self, data: dict):
        """Обробляє завершення обробки переривання."""
        blocked_process = data['blocked_process']
        self.log(f"Interrupt: handled, unblocking process {blocked_process.pid}")
        
        blocked_process.state = "READY"
        blocked_process.advance()
        
        self.current_io_request = None
        self.start_disk_operation()
    
    def handle_process_compute(self, data: dict):
        """Обробляє виконання обчислень процесом."""
        process = data['process']
        self.log(f"Process {process.pid}: computing data ({self.compute_time} ms)")
        
        process.quantum_remaining -= self.compute_time
        
        if process.quantum_remaining <= 0:
            self.log(f"Process {process.pid}: quantum expired")
            self.schedule_next_process()
        else:
            if not process.is_finished():
                req = process.get_next_request()
                req_type, sector = req
                self.schedule_event(0, EventType.SYSCALL_START, {
                    'process': process, 'req_type': req_type, 'sector': sector
                })
            else:
                process.state = "FINISHED"
                self.log(f"Process {process.pid}: FINISHED")
                self.statistics.process_finished(process.pid)
                self.schedule_next_process()
    
    def schedule_next_process(self):
        """Планує виконання наступного готового процесу за алгоритмом Round Robin."""
        ready_processes = [p for p in self.processes if p.state == "READY"]
        
        if not ready_processes:
            self.log("Scheduler: no ready processes")
            self.current_process = None
            return
        
        next_process = ready_processes[0]
        self.schedule_event(0, EventType.PROCESS_START, {'process': next_process})

