import time

'''
from https://realpython.com/python-timer/ + custom functions
'''


class TimerError(Exception):
    """A custom exception used to report errors in use of Timer class"""


class Timer:
    def __init__(self):
        self._start_time = None
        self._last_lap = None
        self._lap_number = 1

    def start(self):
        """Start a new timer"""
        if self._start_time is not None:
            raise TimerError(f"Timer is running. Use .stop() to stop it")

        self._start_time = time.perf_counter()
        self._last_lap = self._start_time

    def stop(self):
        """Stop the timer, and report the elapsed time"""
        if self._start_time is None:
            raise TimerError(f"Timer is not running. Use .start() to start it")

        elapsed_time = time.perf_counter() - self._start_time
        self._start_time = None
        print(f"Elapsed time: {elapsed_time:0.4f} seconds")

    def lap(self):
        if self._start_time is None:
            raise TimerError(f"Timer is not running. Use .start() to start it")

        lap_time = time.perf_counter() - self._last_lap
        self._last_lap = time.perf_counter()
        print(f"Lap {self._lap_number} time: {lap_time:0.4f} seconds")
        self._lap_number += 1
