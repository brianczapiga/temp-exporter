#!/usr/bin/python3

import glob
import os
import board
import sys
import daemon
import time
from pid import PidFile
from prometheus_client import start_http_server, Gauge

location = None
hostname = os.uname()[1]
port = 8367

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f

TEMP = Gauge('temperature', 'DS18B20 Temperature Celsius', ['location','hostname','unit'])

if __name__ == '__main__':
  print("Starting server on " + str(port) + "...")
  with daemon.DaemonContext():
    start_http_server(port)

    while True:
      (c, f) = read_temp()
      TEMP.labels(location=location, hostname=hostname, unit='c').set(c)
      TEMP.labels(location=location, hostname=hostname, unit='f').set(f)
      time.sleep(1)
