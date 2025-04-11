import time

from dispatcher import Dispatcher
from boiler_state_reader import BoilerStateReader
from p1_state_reader import P1StateReader
from homeassist_state_reader import HomeassistStateReader

from state import State

state = State()

def main():
    dispatcher = Dispatcher(state)
    boiler_state_reader = BoilerStateReader(state)
    p1_state_reader = P1StateReader(state)
    homeassist_state_reader = HomeassistStateReader(state)

    try:
        p1_state_reader.start()
        boiler_state_reader.start()
        time.sleep(1)
        dispatcher.start()
        homeassist_state_reader.start()

        p1_state_reader.join()
        boiler_state_reader.join()
        dispatcher.join()
        homeassist_state_reader.join()
    except KeyboardInterrupt:
        print("Main thread terminated by user.")

if __name__ == "__main__":
    main()
