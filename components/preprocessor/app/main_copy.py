#import inline_phase
import time
from manage_data import ManageData
import inline_phase



if __name__ == '__main__':
    manager = ManageData()
    time.sleep(5)
    #training_data = training_phase.start_training()
    #print(training_data)
    #manager.write_to_database(data=training_data)
    data_head, data_trainig = manager.read_from_database_input()
    manager.read_from_database_training()

    print(data_trainig)



    inline_phase.start_inline_phase(kopfzeile=data_head, matrix=data_trainig)

    #damit der Container zum debuggen online bleibt
    time.sleep(100)

    while True:
        print('while')
        time.sleep(1)
