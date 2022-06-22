import multiprocessing as mp
import time

def process():
    while True:
        print('working')
        time.sleep(1)

if __name__ == '__main__':
    p1 = mp.Process(target=process)
    p1.start()
    time.sleep(5)
    p1.terminate()