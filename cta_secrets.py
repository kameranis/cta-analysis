import os
import sys


directory = os.path.dirname(os.path.realpath(__file__))
BUS_API_KEY_FILE = os.path.join(directory, "bus_api_key.txt")
TRAIN_API_KEY_FILE = os.path.join(directory, "train_api_key.txt")

if not os.path.exists(BUS_API_KEY_FILE):
    bus_api_key = input("No bus API key detected. Enter your bus API key or Ctlr+C to exit: ")
    if len(bus_api_key) != 25:
        print("Bus API keys are 25 characters long. Length mismatch. Exiting...")
        sys.exit()
    else:
        with open(BUS_API_KEY_FILE, "w") as f:
            print(bus_api_key, file=f, end='')

with open(os.path.join(directory, "bus_api_key.txt"), "r") as f:
    BUS_API_KEY = f.readline().rstrip()


if not os.path.exists(TRAIN_API_KEY_FILE):
    train_api_key = input("No train API key detected. Enter your train API key or Ctlr+C to exit: ")
    if len(train_api_key) != 32:
        print("Train API keys are 32 characters long. Length mismatch. Exiting...")
        sys.exit()
    else:
        with open(TRAIN_API_KEY_FILE, "w") as f:
            print(train_api_key, file=f, end='')
with open(os.path.join(directory, "train_api_key.txt"), "r") as f:
    TRAIN_API_KEY = f.readline().rstrip()
