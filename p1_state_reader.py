import datetime
import threading
import time

from state import State

P1_FILE_PATH = '/opt/tmpfs/demo.txt'

def extract_value(value_code, response_lines):
    value = 0
    for line in response_lines:
        if line.startswith(value_code):
            value_start = line.find('(') + 1
            value_end = line.find('*', value_start)
            extracted_value_str = line[value_start:value_end].strip()
            value = int(float(extracted_value_str) * 1000)
    return value

def load_inst_import(response_lines):
    inst_import = []
    inst_import.append(extract_value("1-0:21.7.0", response_lines))
    inst_import.append(extract_value("1-0:41.7.0", response_lines))
    inst_import.append(extract_value("1-0:61.7.0", response_lines))
    return inst_import

def load_inst_export(response_lines):
    inst_export = []
    inst_export.append(extract_value("1-0:22.7.0", response_lines))
    inst_export.append(extract_value("1-0:42.7.0", response_lines))
    inst_export.append(extract_value("1-0:62.7.0", response_lines))
    return inst_export

def load_total_exported(response_lines):
    export = extract_value("1-0:2.8.0", response_lines)
    return export
#    export_day = extract_value("1-0:2.8.1", response_lines)
#    export_night = extract_value("1-0:2.8.2", response_lines)
#    return export_day + export_night


class P1StateReader(threading.Thread):
    def __init__(self, state):
        super().__init__()
        self.state = state

    def run(self):
        print("Starting p1 reader...")
        print_counter = 0
        while True:
            try:
                with open(P1_FILE_PATH, 'r') as file:
                    value = file.read()
                response_lines = value.splitlines()
                with self.state.p1_power_lock:
                    current_exported = load_total_exported(response_lines)
                    if current_exported == 0:
                        time.sleep(0.1)
                        continue

                    self.state.current_exported = current_exported


                    self.state.p1_state_time = datetime.datetime.now()
                    self.state.inst_import = load_inst_import(response_lines)
                    self.state.inst_import_total = sum(self.state.inst_import)

                    self.state.inst_export = load_inst_export(response_lines)
                    self.state.inst_export_total = sum(self.state.inst_export)

                    self.state.inst_balance = list(map(lambda x, y: x - y, self.state.inst_import, self.state.inst_export))
                    self.state.inst_balance_total = sum(self.state.inst_balance)

                    if print_counter == 0:
                        print(f"{self.state.p1_state_time} Live: {self.state.inst_balance_total:>6}W [{self.state.inst_balance[0]:>5}W {self.state.inst_balance[1]:>5}W {self.state.inst_balance[2]:>5}W]")
                        print_counter = 50
                    print_counter = print_counter - 1

                ## TODO change to 1 second and reduce logging
                time.sleep(0.2)
            except KeyboardInterrupt:
                print("Dispatcher terminated by user.")
                break
            except Exception as error:
                print("Unexpected error.", error)
                time.sleep(1)
