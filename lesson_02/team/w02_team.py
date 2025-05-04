"""
Course: CSE 351 
Lesson: L02 team activity
File:   prove.py
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
- Create a threaded class to make a call to the server where
  it retrieves data based on a URL.  The class should have a method
  called get_name() that returns the name of the character, planet, etc...
- The threaded class should only retrieve one URL.
  
- Speed up this program as fast as you can by:
    - creating as many as you can
    - start them all
    - join them all

"""

from datetime import datetime, timedelta
import threading

from common import *

# Include cse 351 common Python files
from cse351 import *

# global
call_count = 0
threads = []

class GetInfo(threading.Thread):
    def __init__(self, url):
        super().__init__()
        self.name = ''
        self.url = url

    def run(self):
        item = get_data_from_server(self.url)
        self.name = item['name']

    def get_name(self):
        return self.name
    
# class GetUrls(threading.Thread):
#     def __init__ (self, kind, film6):
#         super().__init__()
#         self.kind = kind
#         self.film6 = film6
#         self._lock = threading.Lock()
#         self.items = []


#     def run(self):
#         global call_count

        
#         urls = self.film6[self.kind]
#         #print(self.name)
#         for url in urls:
#             with self._lock:
#                 call_count += 1
#                 item = get_data_from_server(url)
#                 self.items.append(item['name'])
#                 # print(f"  - {item['name']}")
                

    
#     def Get_Name(self):
#         return self.name


def get_urls(film6, kind):
    global call_count
    global threads

    urls = film6[kind]
    print(kind)
    for url in urls:
        call_count += 1
        # t = threading.Thread(target=get_data_from_server, args=(url, ))
        t = GetInfo(url)
        threads.append(t)
        t.start()        

        # item = get_data_from_server(url)
        # print(f"  - {item['name']}")

def main():
    global call_count

    log = Log(show_terminal=True)
    log.start_timer('Starting to retrieve data from the server')

    film6 = get_data_from_server(f'{TOP_API_URL}/films/6')
    call_count += 1
    print_dict(film6)

    # character_thread = GetUrls('characters', film6)
    # planet_thread = GetUrls('planets', film6)
    # starship_thread = GetUrls('starships', film6)
    # vehicle_thread = GetUrls('vehicles', film6)
    # species_thread = GetUrls('species', film6)

    # threads = []

    # for t in [character_thread, planet_thread, starship_thread, vehicle_thread, species_thread]:
    #     t.start()
    #     threads.append(t)

    # for t in threads:
    #     t.join()
    #     print(f"{t.kind}: {t.items}")

    # Retrieve people
    get_urls(film6, 'characters')
    get_urls(film6, 'planets')
    get_urls(film6, 'starships')
    get_urls(film6, 'vehicles')
    get_urls(film6, 'species')

    for t in threads:
        t.join()
        print(f"  - {t.get_name()}")

    log.stop_timer('Total Time To complete')
    log.write(f'There were {call_count} calls to the server')

if __name__ == "__main__":
    main()