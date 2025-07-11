""" 
Course: CSE 351
Lesson: L05 Team Activity
File:   team.py
Author: <Add name here>
Purpose: Find prime numbers

Instructions:

- Don't include any other Python packages or modules
- Review and follow the team activity instructions (team.md)
"""

from datetime import datetime, timedelta
import multiprocessing as mp
import random
from matplotlib.pylab import plt  # load plot library


# Include cse 351 common Python files
from cse351 import *

def is_prime(n):
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

def main():
    global PROCESSES
    log = Log(show_terminal=True)
    log.start_timer()

    print(f'{mp.cpu_count()} CPU COUNT')

    xaxis_cpus = []
    yaxis_times = []

    

    start = 10000000000
    range_count = 100000
    numbers_processed = 0
    list_of_all_numbers = [i for i in range(start, start + range_count)]
    
    print(flush=True)

    
    PROCESSES = 1
    while PROCESSES <= mp.cpu_count():
        start_time = time.time()
        p = mp.Pool(PROCESSES)

        with p:
            p.map(is_prime, list_of_all_numbers)

        end_time = time.time()
        elapsed_time = end_time - start_time

        xaxis_cpus.append(PROCESSES)
        yaxis_times.append(elapsed_time)

        print(f'Processes done: {PROCESSES} Time elapsed: {elapsed_time}')

        PROCESSES += 1



    

    # create plot of results and also save it to a PNG file
    plt.plot(xaxis_cpus, yaxis_times)
    
    plt.title('Time VS CPUs')
    plt.xlabel('CPU Cores')
    plt.ylabel('Seconds')
    plt.legend(loc='best')

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()
