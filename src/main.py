from threading import Thread, Semaphore
from datetime import datetime
import sys

is_primes = []

semaphore = Semaphore()

class SieveThread(Thread):
    def __init__(self):
        Thread.__init__(self)
    
    def run(self, index=None, limit=None):
        if index and limit:
            semaphore.acquire()

            for i in range(index * index, limit + 1, index):
                is_primes[i] = False

            semaphore.release()


def sieve_eratosthenes(limit, threads):
    for _ in range(limit + 1):
        is_primes.append(True)

    is_primes[0] = False

    is_primes[1] = False

    p = 2

    while (p * p <= limit):
        if (is_primes[p] == True):
            index_thread = p % len(threads)

            threads[index_thread].run(p, limit)

        p += 1

if __name__ == '__main__':
    number_of_threads = int(sys.argv[1])
    
    limit = int(sys.argv[2])

    begin = datetime.now()

    threads = []

    for _ in range(number_of_threads):
        thread = SieveThread()

        threads.append(thread)

        thread.start()

    sieve_eratosthenes(limit, threads)

    for thread in threads:
        thread.join()
    
    end = datetime.now()

    time = (end - begin).total_seconds()

    with open(f'../doc/log.txt', 'a') as file_object:
        file_object.write(f'Time: {time} seg, Number of threads: {number_of_threads}, Limit: {limit}\n')

        file_object.close()

    primes = [number for number, is_prime in enumerate(is_primes) if is_prime]

    print(primes)