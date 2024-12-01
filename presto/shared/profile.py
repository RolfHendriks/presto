# profile.py
# A simple time profiler to create timestamped log messages
import time

class Profiler:
    def __init__(self):
        self._timestamp = time.perf_counter()
    
    def log(self, message):
        elapsed = time.perf_counter() - self._timestamp
        print(f"{elapsed:.3f}:\t{message}")

    def start(self):
        self._timestamp = time.perf_counter()
    