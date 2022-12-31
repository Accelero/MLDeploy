import learning_phase
import time

if __name__ == '__main__':
    time.sleep(10)
    learning_data = learning_phase.start_learning()
    print(learning_data)

    # while True:
    #     print('while')