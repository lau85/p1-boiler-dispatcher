import datetime
import json
import requests
import threading
import time
import state

def read_line(response):
    full_response = ""
    for chunk in response.iter_content(chunk_size=1):
        if chunk:  # Filter out keep-alive chunks
            try:
                symbol = chunk.decode("utf-8")
            except:
                continue
        if '\n' in symbol:
            break
        else:
            full_response += symbol

    return full_response

def make_data_object(line):
    if 'data' in line and '{' in line:
        try:
            json_text = line.split(":", 1)[1]
            return json.loads(json_text)
        except:
            return None
    else:
        return None


def read_temperature_value():
    trycount = 5
    while trycount > 0:
        trycount -= 1
        try:
            response = requests.get('http://10.0.0.191/events', stream=True, timeout=5)
            if response.status_code == 200:
                while True:
                    line = read_line(response)
                    data_object = make_data_object(line)
                    if data_object is not None and 'id' in data_object and "sensor-boiler_temperature" == data_object["id"]:
                        return data_object['value']
            else:
                if trycount == 0:
                    print("Failed to retrieve data. Status code:", response.status_code)
        except Exception as error:
            if trycount == 0:
                print(error)
        time.sleep(1)
    return None


def read_average_temperature():
    while True:
        temperature_a = read_temperature_value()
        if temperature_a is None:
            continue
        print(f"T1 A: {temperature_a}")
        time.sleep(3)
        temperature_b = read_temperature_value()
        if temperature_b is None:
            continue
        temperature_difference = temperature_b - temperature_a
        print(f"T1 B: {temperature_b} Diff: {temperature_difference}")
        if abs(temperature_difference) < 1:
            return round(temperature_b, 2)
        else:
            time.sleep(10)


class StateReader(threading.Thread):
    def __init__(self, state):
        super().__init__()
        self.state = state

    def run(self):
        print("Starting temperature reader...")
        global boiler_temperature
        while True:
            try:
                with self.state.boiler_temperature_lock:
                    self.state.boiler_temperature = read_average_temperature()
                    self.state.boiler_temperature_time = datetime.datetime.now()
                time.sleep(30)
            except KeyboardInterrupt:
                print("Temperatire reader terminated by user.")
                break
            except Exception as error:
                print("Unexpected error.", error)
                continue
