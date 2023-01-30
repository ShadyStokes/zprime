import time

def maybe_add_trailing_space(s):
    return f'{s} ' if s != '' else ''

def maybe_add_leading_space(s):
    return f' {s}' if s != '' else ''

def generic_log(name = ''): 
    return lambda i: print(
        f'{maybe_add_trailing_space(name)}{i}'
    )

class Counter:
    def __init__(self, count = 0, interval = 1, log = ''):
        self.count = count
        self.interval = interval
        self.log = generic_log(log) if isinstance(log, str) else log

    def increment(self):
        self.count += 1
        if self.count % self.interval == 0:
            self.log(self.count)
    
    def reset(self):
        self.count = 0


def generic_min_log(before = '', after = ''):
    return lambda t: f'{maybe_add_trailing_space(before)}{round(t / 60, 1)} min{maybe_add_leading_space(after)}'

class Timer:
    def __init__(self, start = time.time(), log = ''):
        self.start = start
        self.log = generic_min_log(before = log) if isinstance(log, str) else log
    
    def elapsed(self):
        return self.log(time.time() - self.start)

    def tell(self):
        print(self.time_elapsed())
    
    def reset(self):
        self.start = time.time()