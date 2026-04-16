import asyncio
import threading


class ScheduledTask:
    """This class is used to schedule a task for both sync and async programming"""
    def __init__(
            self, delay_in_seconds, is_async, method_name, *args, **kwargs):
        self.delay_in_seconds = delay_in_seconds
        self.method_name = method_name
        self.args = args
        self.kwargs = kwargs

        # Event to keep track of when to stop the thread
        self._stop_event = threading.Event()
        # Using daemon so thread runs in background and won't stop application from shutting down
        if is_async:
            self._thread = threading.Thread(
                target=asyncio.run, args=(self._run_async(),), daemon=True)
        else:
            self._thread = threading.Thread(target=self._run_sync, daemon=True)

    async def _run_async(self):
        while not self._stop_event.is_set():
            # Calling the actual method
            await self.method_name(*self.args, **self.kwargs)

            # Waiting for specified number of seconds and then continuing the thread,
            # if in between flag(for _stop_event the set() method is called) is set to true
            # then we break the thread
            if self._stop_event.wait(self.delay_in_seconds):
                break

    def _run_sync(self):
        while not self._stop_event.is_set():
            # Calling the actual method
            self.method_name(*self.args, **self.kwargs)

            # Waiting for specified number of seconds and then continuing the thread,
            # if in between flag(for _stop_event the set() method is called) is set to true
            # then we break the thread
            if self._stop_event.wait(self.delay_in_seconds):
                break

    def start(self):
        # Starts execution of the thread
        self._thread.start()

    def cancel(self):
        # Setting flag in Event class object to true
        self._stop_event.set()
        # Waits for thread to finish cleanly
        self._thread.join()
