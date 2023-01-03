import learning_phase
import time
from manage_data import ManageData



if __name__ == '__main__':
    manager = ManageData()
    time.sleep(5)
    learning_data = learning_phase.start_learning()
    print(learning_data)
    manager.write_to_database(data=learning_data)
    manager.read_from_database()

    #damit der Container zum debuggen online bleibt
    time.sleep(1000)
