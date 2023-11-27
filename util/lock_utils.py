from multiprocessing import Lock

def locked(lock: Lock) -> bool:
    acquired = lock.acquire(False) # non-blocking
    if acquired:
        lock.release()
    return not acquired 