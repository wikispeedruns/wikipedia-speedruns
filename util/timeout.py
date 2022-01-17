import sys
import time

### NOTE
# I originally wanted to use multithreading to track time, similar to:
# https://docs.python.org/3/library/multiprocessing.html
# https://stackoverflow.com/questions/21827874/timeout-a-function-windows
# But it doesn't seem like flask likes that, so I can only use a single thread timer that checks the start time as the process proceeds


class TimeoutError(RuntimeError):
    """Function Timed-out"""


def timer(timeout, code, *args, **kwargs):
    "Time-limited execution."
    def tracer(frame, event, arg, start=time.time()):
        "Helper."
        now = time.time()
        if now > start + timeout:
            raise TimeoutError(f"Function timed out: {start}, {now}")
        return tracer if event == "call" else None

    old_tracer = sys.gettrace()
    try:
        sys.settrace(tracer)
        output = code(*args, **kwargs)
    finally:
        sys.settrace(old_tracer)
        
    return output