from typing import List, TextIO, Callable
import sched
import time

import pandas as pd

import bus
import train


BUS_CALL_INTERVAL = 150
TRAIN_CALL_INTERVAL = 30
BUS_OUTPUT_FILE = 'bus_tracking.csv'
TRAIN_OUTPUT_FILE = 'train_tracking.csv'


def track_buses(out_f: TextIO) -> None:
    vehicles = bus.get_all_vehicles()
    df = pd.DataFrame(vehicles)
    df.to_csv(out_f, header=False, index=False)


def track_trains(out_f: TextIO) -> None:
    trains = train.get_locations()
    df = pd.DataFrame(trains)
    df.to_csv(out_f, header=False, index=False)


def repeated_tracker(func: Callable[[TextIO], None], scheduler: sched.scheduler, out_f: TextIO, call_interval: float = BUS_CALL_INTERVAL) -> None:
    scheduler.enter(call_interval, 1, repeated_tracker, (func, scheduler, out_f, call_interval))
    func(out_f)


def main():
    bus_file = open(BUS_OUTPUT_FILE, 'a')
    train_file = open(TRAIN_OUTPUT_FILE, 'a')
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(0, 1, repeated_tracker, (track_buses, scheduler, bus_file, BUS_CALL_INTERVAL))
    scheduler.enter(0, 1, repeated_tracker, (track_trains, scheduler, train_file, TRAIN_CALL_INTERVAL))
    scheduler.run(blocking=True)


if __name__ == '__main__':
    main()
