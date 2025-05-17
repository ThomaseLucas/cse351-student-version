"""
Course    : CSE 351
Assignment: 04
Student   : Thomas Lucas

Instructions:
    - review instructions in the course

In order to retrieve a weather record from the server, Use the URL:

f'{TOP_API_URL}/record/{name}/{recno}

where:

name: name of the city
recno: record number starting from 0

"""

import time
from common import *
import queue
from cse351 import *

THREADS = 5000        # TODO - set for your program
WORKERS = 10
RECORDS_TO_RETRIEVE = 5000  # Don't change


# ---------------------------------------------------------------------------
def retrieve_weather_data(q, q1_space_available, q1_has_item, q2_space_available, q2_has_item, worker_q, barrier):
    '''
    This threaded function will wait until there is something in the queue, then when something is there, it puts in a request to the server
    to retreieve the data based on the given command in the queue. 

    Order should not matter yet, as long as the commands are in the queue.

    This is the structure of a URL that we must build:
    f'{TOP_API_URL}/record/{name}/{recno}
    '''

    while True:
        q1_has_item.acquire()
        command = q.get()
        q1_space_available.release()

        if command == 'All done':
            print('all done')
            q1_space_available.acquire()
            q.put('All done')
            q1_has_item.release()
            break
        
        name = command[0]
        recno = command[1]
        url = f'{TOP_API_URL}/record/{name}/{recno}'

        data = get_data_from_server(url)
        

        q2_space_available.acquire()    
        worker_q.put(data)
        q2_has_item.release()

    if barrier.wait() == 0:
        q2_space_available.acquire()
        worker_q.put('All done')
        q2_has_item.release()

class Worker(threading.Thread):
    def __init__(self, q2_space_available, q2_has_item, worker_q, noaa):
        super().__init__()
        self.q2_space_available = q2_space_available
        self.q2_has_item = q2_has_item
        self.worker_q = worker_q
        self.noaa = noaa


    def run(self):
        while True:
            self.q2_has_item.acquire()
            command = self.worker_q.get()
            self.q2_space_available.release()

            # print(self,command)

            if command == 'All done':
                self.q2_space_available.acquire()
                self.worker_q.put('All done')
                self.q2_has_item.release()
                break

            self.noaa.store_city_details(command['city'], command['date'], command['temp'])



# ---------------------------------------------------------------------------
# TODO - Complete this class
class NOAA:

    def __init__(self):
        self.city_data = {}
        self.lock = threading.Lock()
        

    def store_city_details(self, city, date, temp):
        self.lock.acquire()
        if city not in self.city_data:
            self.city_data[city] = []

        self.city_data[city].append((date, temp))
        self.lock.release()

    def get_temp_details(self, city):
        total_temp = 0
        amount = 0
        
        for data in self.city_data[city]:
            total_temp += data[1]
            amount += 1

        return total_temp / amount

        


# ---------------------------------------------------------------------------
def verify_noaa_results(noaa):

    answers = {
        'sandiego': 14.5004,
        'philadelphia': 14.865,
        'san_antonio': 14.638,
        'san_jose': 14.5756,
        'new_york': 14.6472,
        'houston': 14.591,
        'dallas': 14.835,
        'chicago': 14.6584,
        'los_angeles': 15.2346,
        'phoenix': 12.4404,
    }

    print()
    print('NOAA Results: Verifying Results')
    print('===================================')
    for name in CITIES:
        answer = answers[name]
        avg = noaa.get_temp_details(name)

        if abs(avg - answer) > 0.00001:
            msg = f'FAILED  Expected {answer}'
        else:
            msg = f'PASSED'
        print(f'{name:>15}: {avg:<10} {msg}')
    print('===================================')


# ---------------------------------------------------------------------------
def main():

    log = Log(show_terminal=True, filename_log='assignment.log')
    log.start_timer()

    noaa = NOAA()

    # Start server
    data = get_data_from_server(f'{TOP_API_URL}/start')

    # Get all cities number of records
    print('Retrieving city details')
    city_details = {}
    name = 'City'
    print(f'{name:>15}: Records')
    print('===================================')
    for name in CITIES:
        city_details[name] = get_data_from_server(f'{TOP_API_URL}/city/{name}')
        print(f'{name:>15}: Records = {city_details[name]["records"]:,}')
    print('===================================')

    records = RECORDS_TO_RETRIEVE

    # TODO - Create any queues, pipes, locks, barriers you need
    main_queue = queue.Queue()
    worker_queue = queue.Queue()

    q1_space_available = threading.Semaphore(10)
    q1_has_item = threading.Semaphore(0)

    q2_space_available = threading.Semaphore(WORKERS)
    q2_has_item = threading.Semaphore(0)

    thread_barrier = threading.Barrier(THREADS)



    retrieve_threads = []
    worker_threads = []

    #starting up the worker threads
    for i in range(WORKERS):
        t = Worker(q2_space_available, q2_has_item, worker_queue, noaa)
        worker_threads.append(t)
        t.start()

    #starting up the threaded function threads to retrieve weather data
    for i in range(THREADS):
        t = threading.Thread(target=retrieve_weather_data, args=(main_queue, q1_space_available, q1_has_item, q2_space_available, q2_has_item, worker_queue, thread_barrier))
        retrieve_threads.append(t)
        t.start()

    for city in CITIES:
        for i in range(records):
            q1_space_available.acquire()
            main_queue.put((city, i))
            q1_has_item.release()
            
    q1_space_available.acquire()
    main_queue.put('All done')
    q1_has_item.release()

    print(main_queue)

    for i in retrieve_threads:
        t.join()

    for i in worker_threads:
        t.join()

    print(main_queue.qsize())
    print('finished loading the commands')

    # End server - don't change below
    data = get_data_from_server(f'{TOP_API_URL}/end')
    print(data)

    verify_noaa_results(noaa)

    log.stop_timer('Run time: ')


if __name__ == '__main__':
    main()

