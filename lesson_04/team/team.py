""" 
Course: CSE 351
Team  : Week 04
File  : team.py
Author: <Student Name>

See instructions in canvas for this team activity.

"""

import random
import threading

# Include CSE 351 common Python files. 
from cse351 import *

# Constants
MAX_QUEUE_SIZE = 10
PRIME_COUNT = 1000
FILENAME = 'primes.txt'
PRODUCERS = 3
CONSUMERS = 5

# ---------------------------------------------------------------------------
def is_prime(n: int):
    if n <= 3:
        return n > 1
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i ** 2 <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

# ---------------------------------------------------------------------------
class Queue351():
    """ This is the queue object to use for this class. Do not modify!! """

    def __init__(self):
        self.__items = []
   
    def put(self, item):
        assert len(self.__items) <= 10
        self.__items.append(item)

    def get(self):
        return self.__items.pop(0)

    def get_size(self):
        """ Return the size of the queue like queue.Queue does -> Approx size """
        extra = 1 if random.randint(1, 50) == 1 else 0
        if extra > 0:
            extra *= -1 if random.randint(1, 2) == 1 else 1
        return len(self.__items) + extra

# ---------------------------------------------------------------------------
def producer(q, filled, present, barrier):
    for i in range(PRIME_COUNT):
        number = random.randint(1, 1_000_000_000_000)
        
        filled.acquire()
        q.put(number)
        present.release()
        
    if barrier.wait() == 0:
        q.put('All done')
        present.release()
        print('all done')

# ---------------------------------------------------------------------------
def consumer(q, filled, present):
    while True:
        present.acquire()
        value = q.get()
        filled.release()

        if value == 'All done':
            q.put('All done')
            present.release()
            break

        if is_prime(value):
                with open(FILENAME, 'a') as prime_f:
                    prime_f.write(str(value))
                    prime_f.write('\n')
# ---------------------------------------------------------------------------
def main():
    with open(FILENAME, 'w'):
        pass

    random.seed(102030)

    que = Queue351()

    queue_filled = threading.Semaphore(MAX_QUEUE_SIZE)

    anything_present = threading.Semaphore(0) # TODO Find out what this one is for


    producer_barrier = threading.Barrier(PRODUCERS)

    p_threads = []
    c_threads = []

    for i in range(PRODUCERS):
        t = threading.Thread(target=producer, args=(que, queue_filled, anything_present, producer_barrier))
        p_threads.append(t)
        t.start()

    for i in range(CONSUMERS):
        t = threading.Thread(target=consumer, args=(que, queue_filled, anything_present))
        c_threads.append(t)
        t.start()

    for t in p_threads:
        t.join()

    for t in c_threads:
        t.join()

    if os.path.exists(FILENAME):
        with open(FILENAME, 'r') as f:
            primes = len(f.readlines())
    else:
        primes = 0
    print(f"Found {primes} primes. Should be {108}.")



if __name__ == '__main__':
    main()
