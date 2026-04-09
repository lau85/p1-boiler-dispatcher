import datetime
import requests
import threading
import time
import state
import config

# Home Assistant configuration
ENTITY_IDS = {
    "max_export_to_grid_power_boiler": "input_number.max_export_to_grid_power_boiler",
    "max_export_to_grid_power_boiler_buffer": "input_number.max_export_to_grid_power_boiler_buffer",
    "min_boiler_temperature": "input_number.min_boiler_temperature",
    "boiler_mode": "input_select.boiler_mode"

}

def get_state(entity_id):
    url = f"{config.HOME_ASSISTANT_URL}/api/states/{entity_id}"
    headers = {
        "Authorization": f"Bearer {config.ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers, timeout=5)
    if response.status_code == 200:
        return response.json().get("state")
    else:
        raise RuntimeError(
            f"Error fetching state for {entity_id}: {response.status_code} {response.text}"
        )

class HomeassistStateReader(threading.Thread):
    def __init__(self, state):
        super().__init__()
        self.state = state

    def run(self):
        print("Starting homeassistant state reader...")
        while True:
            try:
                with self.state.homeassist_state_lock:
                    self.state.homeassist_max_export_power = int(float(get_state(ENTITY_IDS["max_export_to_grid_power_boiler"])))
                    self.state.homeassist_max_export_power_buffer = int(float(get_state(ENTITY_IDS["max_export_to_grid_power_boiler_buffer"])))
                    self.state.homeassist_min_boiler_temperature = int(float(get_state(ENTITY_IDS["min_boiler_temperature"])))
                    self.state.homeassist_boiler_mode = get_state(ENTITY_IDS["boiler_mode"])
                    print(f"max_export_to_grid_power_boiler: {self.state.homeassist_max_export_power} max_export_to_grid_power_boiler_buffer: {self.state.homeassist_max_export_power_buffer}\n")
                time.sleep(15)
            except KeyboardInterrupt:
                print("Homeassist state reader terminated by user.")
                break
            except Exception as error:
                print("Unexpected error.", error)
                continue
