# python 2.7
from matplotlib import pyplot as plt
import scipy
import numpy
import tkinter as tk
from tkinter import filedialog
import csv
from datetime import datetime
import time

# Convert a date-time string into a timestamp in seconds
def fix_timestamp(datetime_str):
    datetime_list = list(datetime_str.split(" "))
    timestamp_str = datetime_list[1]
    h, m, s = timestamp_str.split(':')
    return float(h) * 3600.0 + float(m) * 60.0 + float(s)

root = tk.Tk()
root.withdraw()

file_path = filedialog.askopenfilename()
print("You are viewing: " + file_path)
"""
    Logs will have the following format:
        Time,Wind Speed,Horizontal Direction,Vertical Direction,Temperature,Pressure,Pitch,Roll,Magnetic Heading 
        Time stamp is HH::mm::ss
        Date is YY-MM-DD
"""
time_stamps = []
wind_speed = []
pitch = []
roll = []
with open(file_path) as datafile:
    csv_reader = csv.reader(datafile, delimiter=',')
    for row in csv_reader:
        datetime_str = row[0]
        time_stamps.append(fix_timestamp(datetime_str))
        wind_speed.append(row[1])
        pitch.append(row[6])
        roll.append(row[7])

fig1, ax1 = plt.subplots()
ax1.plot(time_stamps, pitch)
ax1.set_title("Pitch")

fig2, ax2 = plt.subplots()
ax2.plot(time_stamps, roll)
ax2.set_title("Roll")


fig3, ax3 = plt.subplots()
ax3.plot(time_stamps, wind_speed)
ax3.set_title("Wind Speed")



plt.show()