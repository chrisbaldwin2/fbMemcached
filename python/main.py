from python.cache import MemcachedInterface
import random
import string
from abc import ABC, abstractmethod
import time
import tqdm

"""
10 Million SET to populate

ETC:
5% SET
95% GET

Key size is 16 bytes
90% values evenly distributed between 16 and 512 bytes
10% values between 512-10_000 bytes

SYS:
25% SET 
75% GET

40% key are 16-20 bytes
60% keys are 20-45 bytes

80% of values are between 320-500 bytes
8% are smaller
12% are between 500-10_000 bytes
"""


# Might want to add random seed for reproducibility
class Tester(ABC):
    def __init__(self, cache: MemcachedInterface | None = None, test=False):
        self.test = test
        if cache == None:
            self.cache = MemcachedInterface()
        else:
            self.cache = cache
        self.num_entries = 10_000_000 if not test else 100_000
    @abstractmethod
    def main(self) -> bool:
        pass
    @abstractmethod
    def load(self) -> None:
        pass
    @abstractmethod
    def run(self) -> None:
        pass
    @abstractmethod
    def key(self, index: int) -> str:
        pass
    @abstractmethod
    def key_size(self, index: int) -> int:
        pass
    @abstractmethod
    def value(self, index: int) -> str:
        pass
    @abstractmethod
    def value_size(self, index: int) -> int:
        pass
    @abstractmethod
    def print(*args, **kwargs) -> None:
        pass
    def random_value(self, size: int):
        return ''.join(random.choice(string.ascii_letters) for _ in range(size))
    def print(self, *args, **kwargs):
        if self.test:
            print(*args, **kwargs)

class ETC(Tester):
    def __init__(self, cache: MemcachedInterface | None = None, test=False):
        super().__init__(cache, test)

    def key_size(self, index: int):
        return 16
    
    def value_size(self, index: int):
        pct = index / self.num_entries
        if pct < 0.9:
            return int(16 + pct * 496)
        if pct < 0.98:
            return int(512 + (pct - 0.9) * 9_488)
        return int(10_000 + (pct - 0.98) * 90_000)
    
    def key(self, index: int):
        return f'{index:0<{self.key_size(index)}}'
    
    def value(self, index: int):
        return self.random_value(self.value_size(index))

    def load(self):
        self.cache.clear()
        for i in tqdm.tqdm(range(self.num_entries)):
            self.cache.set(f'{self.key(i)}', f'{self.value(i)}', ttl=0)

    def run(self):
        for i in tqdm.tqdm(range(self.num_entries)):
            if random.random() < 0.05:
                self.cache.set(f'{self.key(i)}', f'{self.value(i)}', ttl=0)
            else:
                value = self.cache.get(f'{self.key(i)}')
                # self.print(f"{self.key(i)}:{value}")

    def main(self):
        print('Starting to load data')
        try:
            self.load()
        except Exception as e:
            print(f'\n\n ~~~~Hit Exception during load phase~~~~ \n\n{e}')
            return False
        print('Finished loading data. Starting run')
        try:
            self.run()
        except Exception as e:
            print(f'\n\n ~~~~Hit Exception during run phase~~~~ \n\n{e}')
            return False
        return True
    
class SYS(Tester):
    def __init__(self, cache: MemcachedInterface | None = None, test=False):
        super().__init__(cache, test)

    def key_size(self, index: int):
        pct = index / self.num_entries
        if pct < 0.4:
            return int(16 + pct * 4)
        return int(20 + (pct - 0.4) * 25)
    def value_size(self, index: int):
        pct = index / self.num_entries
        if pct < 0.8:
            return int(320 + pct * 180)
        if pct < 0.88:
            return int(500 + (pct - 0.8) * 500)
        return int(500 + (pct - 0.88) * 9_500)
    
    def key(self, index: int):
        return f'{index:0<{self.key_size(index)}}'
    def value(self, index: int):
        return self.random_value(self.value_size(index))
    def load(self):
        self.cache.clear()
        for i in tqdm.tqdm(range(self.num_entries)):
            self.cache.set(f'{self.key(i)}', f'{self.value(i)}', ttl=0)
    def run(self):
        # Use tqdm to show progress
        for i in tqdm.tqdm(range(self.num_entries)):
            if random.random() < 0.25:
                self.cache.set(f'{self.key(i)}', f'{self.value(i)}', ttl=0)
            else:
                value = self.cache.get(f'{self.key(i)}')
                # self.print(f"{self.key(i)}:{value}")
    def main(self):
        print('Starting to load data')
        try:
            self.load()
        except Exception as e:
            print(f'\n\n ~~~~Hit Exception during load phase~~~~ \n\n{e}')
            return False
        print('Finished loading data. Starting run')
        try:
            self.run()
        except Exception as e:
            print(f'\n\n ~~~~Hit Exception during run phase~~~~ \n\n{e}')
            return False
        return True

def main():
    test = True
    cache = MemcachedInterface()
    start_time = time.time()
    print(f'Starting ETC test at {time.strftime("%H:%M:%S")}')
    etc = ETC(cache, test)
    if etc.main():
        print('ETC passed')
    print(f'ETC took {time.time() - start_time} seconds')
    start_time = time.time()
    print(f'Starting SYS test at {time.strftime("%H:%M:%S")}')
    sys = SYS(cache, test)
    if sys.main():
        print('SYS passed')
    print(f'SYS took {time.time() - start_time} seconds')

if __name__ == '__main__':
    main()