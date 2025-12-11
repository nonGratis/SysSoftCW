"""
Модуль моделювання жорсткого диска.

Реалізує модель магнітного жорсткого диска з розрахунками часових характеристик
операцій читання та запису, включаючи час пошуку доріжки, затримку обертання
та передачу даних.

Автор: Студент
"""

from typing import Tuple


class HardDisk:
    """
    Модель магнітного жорсткого диска з однією пластиною.
    
    Реалізує фізичні характеристики диска та розрахунки часових параметрів
    для операцій позиціювання головки та передачі даних.
    
    Атрибути:
        num_tracks: Загальна кількість доріжок на диску
        sectors_per_track: Кількість секторів на одній доріжці
        seek_time_per_track: Час переміщення головки на одну доріжку (мілісекунди)
        seek_time_to_edge: Час переміщення до крайньої доріжки (мілісекунди)
        rpm: Швидкість обертання пластини (обертів за хвилину)
        rotation_time: Час повного оберту пластини (мілісекунди)
        avg_rotational_latency: Середня затримка обертання (мілісекунди)
        sector_transfer_time: Час передачі одного сектора (мілісекунди)
        current_track: Поточна позиція головки диска (номер доріжки)
    """
    
    def __init__(self, num_tracks: int, sectors_per_track: int,
                 seek_time_per_track: float, seek_time_to_edge: float,
                 rpm: float):
        """
        Ініціалізує модель жорсткого диска з заданими параметрами.
        
        Args:
            num_tracks: Кількість доріжок на диску
            sectors_per_track: Кількість секторів на доріжці
            seek_time_per_track: Час пошуку однієї доріжки (мс)
            seek_time_to_edge: Час переміщення до краю (мс)
            rpm: Швидкість обертання (обертів/хвилину)
        """
        self.num_tracks = num_tracks
        self.sectors_per_track = sectors_per_track
        self.seek_time_per_track = seek_time_per_track
        self.seek_time_to_edge = seek_time_to_edge
        self.rpm = rpm
        
        self.rotation_time = (60 * 1000) / rpm
        self.avg_rotational_latency = self.rotation_time / 2
        self.sector_transfer_time = self.rotation_time / sectors_per_track
        
        self.current_track = 0
    
    def calculate_seek_time(self, target_track: int) -> Tuple[float, str]:
        """
        Розраховує оптимальний час пошуку цільової доріжки.
        
        Метод обчислює три можливі варіанти переміщення головки:
        1. Пряме переміщення від поточної позиції до цільової доріжки
        2. Переміщення через доріжку 0 (початок диска)
        3. Переміщення через крайню доріжку (кінець диска)
        
        Повертається найшвидший варіант із детальним описом маршруту.
        
        Args:
            target_track: Номер цільової доріжки
        
        Returns:
            Кортеж із часу переміщення (мілісекунди) та текстового опису маршруту
        """
        direct_tracks = abs(target_track - self.current_track)
        direct_time = direct_tracks * self.seek_time_per_track
        
        via_start_tracks = abs(self.current_track - 0) + abs(target_track - 0)
        time_via_start = self.seek_time_to_edge + via_start_tracks * self.seek_time_per_track
        
        via_end_tracks = (abs(self.current_track - (self.num_tracks - 1)) +
                         abs(target_track - (self.num_tracks - 1)))
        time_via_end = self.seek_time_to_edge + via_end_tracks * self.seek_time_per_track
        
        if direct_time <= time_via_start and direct_time <= time_via_end:
            return direct_time, f"direct {direct_tracks} tracks"
        elif time_via_start <= time_via_end:
            return time_via_start, f"via track 0 ({via_start_tracks} tracks)"
        else:
            return time_via_end, f"via track {self.num_tracks-1} ({via_end_tracks} tracks)"
    
    def move_head_to(self, target_track: int):
        """
        Переміщує головку диска на цільову доріжку.
        
        Оновлює внутрішній стан об'єкта, встановлюючи нову поточну позицію головки.
        
        Args:
            target_track: Номер доріжки для переміщення
        """
        self.current_track = target_track
    
    def get_disk_info(self) -> str:
        """
        Повертає інформаційний рядок із характеристиками диска.
        
        Returns:
            Текстовий опис параметрів диска
        """
        return (f"HardDisk: {self.num_tracks} tracks, {self.sectors_per_track} sectors/track, "
                f"{self.rpm} RPM, current position: track {self.current_track}")