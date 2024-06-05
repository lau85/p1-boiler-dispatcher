import time

from dispatcher import Dispatcher
from state_reader import StateReader
from p1_state_reader import P1StateReader

from state import State

state = State()

def main():
    dispatcher = Dispatcher(state)
    state_reader = StateReader(state)
    p1_state_reader = P1StateReader(state)


    try:
        p1_state_reader.start()
        state_reader.start()
        time.sleep(1)
        dispatcher.start()

        p1_state_reader.join()
        state_reader.join()
        dispatcher.join()
    except KeyboardInterrupt:
        print("Main thread terminated by user.")

if __name__ == "__main__":
    main()
