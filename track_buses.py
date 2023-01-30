from typing import List, TextIO
import sched
import time

import pandas as pd

import bus

CALL_INTERVAL = 150
BUS_ROUTES_FILE = 'cta_data/bus_numbers.txt'
OUTPUT_FILE = 'bus_tracking.csv'
MAX_ROUTES_PER_CALL = 10


def track_buses(out_f: TextIO) -> None:
    routes = bus.get_routes()
    rts = [rt['rt'] for rt in routes]
    for i in range(0, len(rts), MAX_ROUTES_PER_CALL):
        vehicles = bus.get_vehicles(routes=rts[i:i + MAX_ROUTES_PER_CALL])
        df = pd.DataFrame(vehicles)
        df.to_csv(out_f, header=False, index=False)


def repeated_track_buses(scheduler: sched.scheduler, out_f: TextIO, call_interval: float = CALL_INTERVAL) -> None:
    scheduler.enter(call_interval, 1, repeated_track_buses, (scheduler, out_f, call_interval))
    track_buses(out_f=out_f)


def main():
    with open(OUTPUT_FILE, 'w+') as out_f:
        scheduler = sched.scheduler(time.time, time.sleep)
        scheduler.enter(0, 1, repeated_track_buses, (scheduler, out_f, CALL_INTERVAL))
        scheduler.run()


if __name__ == '__main__':
    main()
