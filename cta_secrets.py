import os

directory = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(directory, "bus_api_key.txt"), "r") as f:
    BUS_API_KEY = f.readline().rstrip()

with open(os.path.join(directory, "train_api_key.txt"), "r") as f:
    TRAIN_API_KEY = f.readline().rstrip()
