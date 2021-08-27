import time


def pause(howlong: float = 3.0) -> None:
    time.sleep(howlong)


def be_long(howlong: float = 3.0) -> int:
    end = time.time() + howlong

    i = 0
    while time.time() < end:
        i = i + 1
        time.sleep(0.1)

    return i
