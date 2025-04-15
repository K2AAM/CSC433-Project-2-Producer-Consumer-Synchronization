# Adam Morehouse
# Ryan Fosco
# Brandon Coulter
# 14 April 2025


import threading
import sys
import time
from collections import deque

# Global variables
fifo = deque()
maxFifo = int(sys.argv[4])  # Maximum FIFO depth from command line
transactionFile = open(sys.argv[1])  # Input file
idCounter = 0  # Counter for internal transaction IDs

# Synchronization primitives
items = threading.Semaphore(0)  # Tracks items in FIFO
spaces = threading.Semaphore(maxFifo)  # Tracks available spaces in FIFO
mutex = threading.Lock()  # Protects FIFO access
eof = False  # End-of-file flag
eof_mutex = threading.Lock()  # Protects eof flag
active_producers = 0  # Tracks active producers
producers_mutex = threading.Lock()  # Protects active_producers
# We use semaphores for FIFO limits and locks to avoid race conditions

# Transaction class
class Transaction:
    def __init__(self, transactionId, producerSleep, consumerSleep, internalId):
        self.transactionId = transactionId
        self.producerSleep = producerSleep
        self.consumerSleep = consumerSleep.strip()
        self.internalId = internalId
         # internalId lets us track the order transactions are processed

# Producer thread function
def threadProducer():
    global idCounter, eof, active_producers
    for line in transactionFile:
        spaces.acquire()  # Wait for space in FIFO
        params = line.split(",")
        
        with mutex:  # Critical section for FIFO append
            idCounter += 1
            t = Transaction(params[0], params[1], params[2], idCounter)
            fifo.append(t)
            print(f'Producer: {t.transactionId} internalId: {t.internalId}')
            # mutex makes sure only one producer adds at a time
        
        items.release()  # Signal item available
        time.sleep(float(t.producerSleep) / 1000)  # Sleep after releasing lock
        # Sleeping outside locks keeps things moving fast
    
    # Signal producer completion
    with producers_mutex:
        active_producers -= 1
        if active_producers == 0:
            with eof_mutex:
                eof = True
            # Release items to wake up consumers to check EOF
            for _ in range(maxFifo):
                spaces.acquire(blocking=False)  # Reduce spaces to prevent over-release
                items.release()
                # This wakes up consumers when all producers are done, fixes hangs
    # We track active_producers to know when the file’s fully read
    
    print('Producer completed')

# Consumer thread function
def threadConsumer():
    global eof
    while True:
        items.acquire()  # Wait for item in FIFO
        # items makes consumers wait if FIFO is empty
        
        with mutex:  # Critical section for FIFO pop
            # Check EOF and empty FIFO
            with eof_mutex:
                if eof and not fifo:
                    break
            if not fifo:  # FIFO empty but not EOF, retry
                items.release()
                continue
            t = fifo.popleft()
            print(f'Consumer: {t.transactionId} internalId: {t.internalId}')
        # Only one consumer grabs a transaction at a time, keeps it safe
        
        spaces.release()  # Signal space available
        
        if int(t.transactionId) == 9999:  # Termination transaction
            with eof_mutex:
                eof = True
            # Wake up other consumers to check EOF
            for _ in range(maxFifo):
                spaces.acquire(blocking=False)  # Prevent over-release
                items.release()
                # This tells other consumers to check EOF, stops them hanging
            break
            # 9999 is our stop signal, like the project asked for
        
        time.sleep(float(t.consumerSleep) / 1000)  # Sleep after releasing lock
    
    print('Consumer completed')

# Main program
def main():
    global active_producers
    threads = []
    
    # Initialize active producers
    with producers_mutex:
        active_producers = int(sys.argv[2])
    # Set up how many producers we start with
    
    # Start producers
    print(f'Transaction file: {sys.argv[1]}')
    print(f'Starting producers: {sys.argv[2]}')
    for _ in range(int(sys.argv[2])):
        t = threading.Thread(target=threadProducer)
        t.start()
        threads.append(t)
    
    # Start consumers
    print(f'Starting consumers: {sys.argv[3]}')
    for _ in range(int(sys.argv[3])):
        t = threading.Thread(target=threadConsumer)
        t.start()
        threads.append(t)
    
    # Wait for all threads to complete
    for t in threads:
        t.join()
        # join waits for everyone to finish before the program quits

if __name__ == "__main__":
    main()