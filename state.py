import datetime
import threading

class State:

    boiler_power_lock = threading.Lock()
    boiler_power = 0
    boiler_power_time = datetime.datetime.strptime('2000-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    boiler_power_request = 0
    boiler_power_request_time = datetime.datetime.strptime('2000-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')

    boiler_temperature = 0
    boiler_temperature_time = datetime.datetime.strptime('2000-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    boiler_temperature_lock = threading.Lock()

    p1_power_lock = threading.Lock()
    p1_state_time = datetime.datetime.strptime('2000-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    inst_import = [0, 0, 0]
    inst_import_total = 0

    inst_export = [0, 0, 0]
    inst_export_total = 0

    inst_balance = [0, 0, 0]
    inst_balance_total = 0

    current_exported = 0


def set_boiler_power(new_power):
    boiler_power = new_power
    boiler_power_time = datetime.datetime.now()

def set_boiler_power_request(new_power):
    boiler_power_request = new_power
    boiler_power_request_time = datetime.datetime.now()

