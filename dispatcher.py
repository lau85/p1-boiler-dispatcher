import datetime
import time
import requests
import threading
import config
from state import State

BOILER_PHASE = 0

MAX_BALANCE_TOTAL = -5000

LOAD_MIN = 150
LOAD_MAX = 255

LOOP_INTERVAL = 3

power = 0
old_power = 0
is_sent = False

empty_file_counter = 0
start_time = None
start_exported = None
required_balance = 0

state = None

def get_min_balance_total():
    return state.homeassist_max_export_power * -1

def get_buffer():
    return state.homeassist_max_export_power_buffer

def set_power(power, old_power, is_sent):
    if (power == LOAD_MIN):
        action = 'turn_off'
    else:
        action = 'turn_on'

    if power != old_power or is_sent == False:
        is_sent = False
        try:
            print(f" Load: {old_power:>3} -> {power:>3}")
            url = f"{config.BOILER_URL}/{action}?brightness={power}"
            requests.post(url)
            is_sent = True
        except Exception as error:
            print("Fail on request:", error)
    else:
        print(f" Load: {power:>3}")
    return is_sent

def correct_power(power):
    global LOAD_MIN
    global LOAD_MAX
    if (power > LOAD_MAX):
        power = LOAD_MAX

    if (power < LOAD_MIN):
        power = LOAD_MIN
    return power

def calculate_required_balance():
    global start_time
    global start_exported
    global MAX_BALANCE_TOTAL
    cycle_exported = 0

    # to reset start_time every 15 minutes.
    # there is a risk, that p1_state_time is not updated if p1 will not respond for longer than 1 minute and start_time will not be reset.
    if start_time is not None and state.p1_state_time.minute % 15 == 0 and start_time.minute != state.p1_state_time.minute:
        start_time = None

    if start_time is None:
        print("Update start_time. ")
        start_time = state.p1_state_time
        start_exported = state.current_exported
        cycle_exported = 0
        cycle_duration = 0
    else:
        cycle_exported = state.current_exported - start_exported
        cycle_duration = state.p1_state_time.timestamp() - start_time.timestamp()

    average = state.current_average

    required_balance = get_min_balance_total() + get_buffer()
    if (cycle_duration > 30):
        # 900 seconds is cycle duration. At the beginning of cycle we will have BUFFER w buffer at the end we have 0W buffer
        buffer = (900 - cycle_duration) / 900 * get_buffer()
        # closer the end, the bigger is correction factor. After first minute it is 1, at the end it is 15
        # it is because after 1 minute we can fix 100W error using 100w correction, at the end we need 1400w correction
        # multiply by 2 to have more aggressive, faster correction
        correction = (get_min_balance_total() + buffer - average) * (cycle_duration / 60)

#        missing_kwh = get_min_balance_total() / 4 - cycle_exported
#        time_left = 900 - cycle_duration
#        optimal_balance = missing_kwh * 4 / time_left * 3600
#        print(f"Optimal: {optimal_balance:>6.0f}W." end = "")

        # to be more aggressive if export over the limit
        if correction > 0:
            correction = correction * 1.5
        if correction > 9999:
            correction = 9999
        if correction < -9999:
            correction = -9999
        required_balance = get_min_balance_total() + correction + buffer
        print(f"Buff: {buffer:>4.0f} Corr: {correction:>5.0f} ", end = "")

    if (required_balance > MAX_BALANCE_TOTAL):
        required_balance = MAX_BALANCE_TOTAL

    print(f"Avg: {average:>7.0f}W. Limit: {required_balance:>6.0f}W. In {cycle_duration:>3.0f}s {cycle_exported:>4}Wh. ", end = "")
    return required_balance

def calculate_power(inst_balance_total, required_balance, power):
    global LOAD_MAX
    global LOAD_MIN
    delta = 0
    if (abs(inst_balance_total - required_balance) > 1000):
        delta = 100
    elif (abs(inst_balance_total - required_balance) > 500):
        delta = 30
    elif (abs(inst_balance_total - required_balance) > 300):
        delta = 20
    elif (abs(inst_balance_total - required_balance) > 200):
        delta = 10
    elif (abs(inst_balance_total - required_balance) > 100):
        delta = 5
    else:
        delta = 1

    if (inst_balance_total < required_balance and power < LOAD_MAX):
        power += delta
    elif inst_balance_total > required_balance + 20 and power > LOAD_MIN:
        power -= delta

# Turn on boiler in the morning and evening to increase temperature before typical showering time.
    power = recalculate_power_by_temperature(power)

    power = correct_power(power)

    return power

def recalculate_power_by_temperature(power):
    global state
    currenttime = datetime.datetime.now()
    temperature_value_age = currenttime.timestamp() - state.boiler_temperature_time.timestamp()
    time_condition_morning = currenttime.hour >= 7 and currenttime.hour < 8
    time_condition_evening = currenttime.hour >= 16 and currenttime.hour < 19
    if float(state.boiler_temperature) < float(state.homeassist_min_boiler_temperature_morning) and temperature_value_age < 60000 and time_condition_morning:
        return 255
    elif float(state.boiler_temperature) < float(state.homeassist_min_boiler_temperature_evening) and temperature_value_age < 60000 and time_condition_evening:
        return 255
    elif float(state.boiler_temperature) < float(state.homeassist_min_boiler_temperature) and temperature_value_age < 60000:
        return 255
    else:
        return power

def dispatcher_loop():
    global power
    global old_power
    global is_sent
    while True:
        try:
            with state.p1_power_lock:
                old_power = power
                required_balance = calculate_required_balance()
                power = calculate_power(state.inst_balance_total, required_balance, power)

            is_sent = set_power(power, old_power, is_sent)
            time.sleep(LOOP_INTERVAL)
        except KeyboardInterrupt:
            print("Dispatcher terminated by user.")
            break
        except Exception as error:
            print("Unexpected error.", error)
            time.sleep(1)


class Dispatcher(threading.Thread):
    def __init__(self, newstate):
        super().__init__()
        global state
        state = newstate
        self.state = newstate

    def run(self):
        print("Starting dispatcher...")
        dispatcher_loop()
