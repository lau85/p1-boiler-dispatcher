import threading

class State:
    boiler_temperature = 0
    boiler_temperature_time = 0
    boiler_temperature_lock = threading.Lock()

    p1_power_lock = threading.Lock()
    p1_state_time = 0
    inst_import = [0, 0, 0]
    inst_import_total = 0

    inst_export = [0, 0, 0]
    inst_export_total = 0

    inst_balance = [0, 0, 0]
    inst_balance_total = 0

    current_exported = 0
