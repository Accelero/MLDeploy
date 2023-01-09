import training_phase
import time
from manage_data import ManageData



if __name__ == '__main__':
    manager = ManageData()
    time.sleep(5)
    training_data = training_phase.start_training()
    print(training_data)
    manager.write_to_database(data=training_data)
    #manager.read_from_database()

    #damit der Container zum debuggen online bleibt
    time.sleep(100)

    while True:
        print('while')
        time.sleep(1)
