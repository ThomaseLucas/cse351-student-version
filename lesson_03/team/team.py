"""
Course: CSE 351 
Lesson: L03 team activity
File:   team.py
Author: <Add name here>

Purpose: Retrieve Star Wars details from a server

Instructions:

- This program requires that the server.py program be started in a terminal window.
- The program will retrieve the names of:
    - characters
    - planets
    - starships
    - vehicles
    - species

- the server will delay the request by 0.5 seconds

TODO
- Create a threaded function to make a call to the server where
  it retrieves data based on a URL.  The function should have a method
  called get_name() that returns the name of the character, planet, etc...
- The threaded function should only retrieve one URL.
- Create a queue that will be used between the main thread and the threaded functions

- Speed up this program as fast as you can by:
    - creating as many as you can
    - start them all
    - join them all

"""

from datetime import datetime, timedelta
import threading
from common import *
import queue

# Include cse 351 common Python files
from cse351 import *

# global
call_count = 0

class GetUrl(threading.Thread):
    def __init__(self, q):
        super().__init__()
        self.q = q
        self.item = None

    def run(self):
        url = self.q.get()

        self.item = get_data_from_server(url)


    def get_name(self):
        return self.item['name']
        

def get_urls(film6, kind, q):
    global call_count

    urls = film6[kind]
    print(kind)
    for url in urls:
        call_count += 1
        q.put(url)

        

def main():
    global call_count

    log = Log(show_terminal=True)
    log.start_timer('Starting to retrieve data from the server')

    film6 = get_data_from_server(f'{TOP_API_URL}/films/6')
    call_count += 1
    print_dict(film6)

    # Retrieve people

    


    q = queue.Queue()

    get_urls(film6, 'characters', q)
    get_urls(film6, 'planets', q)
    get_urls(film6, 'starships', q)
    get_urls(film6, 'vehicles', q)
    get_urls(film6, 'species', q)

    q.put(None)

    threads = []

    while True:
        if q.get() == None:
            break
        else:
            t = GetUrl(q)
            threads.append(t)
            t.start()

    for thread in threads:
        thread.join()
        print(thread.get_name())


    log.stop_timer('Total Time To complete')
    log.write(f'There were {call_count} calls to the server')

if __name__ == "__main__":
    main()
