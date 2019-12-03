# python 2.7
from matplotlib import pyplot as plt
import scipy.fftpack
import numpy
import tkinter as tk
from tkinter import filedialog
import csv
from datetime import datetime
import time

"""
    Program to view and analyze Trinsonica Windspeed sensor logs
"""


# Convert a date-time string into a timestamp in seconds
def fix_timestamp(datetime_str):
    datetime_list = list(datetime_str.split(" "))
    timestamp_str = datetime_list[1]
    h, m, s = timestamp_str.split(':')
    return float(h) * 3600.0 + float(m) * 60.0 + float(s)

# Plot FFT of given set of data
def plot_fft(data, timestamps, title_str):
    # Number of samples
    N = len(data)
    Fs = 5.0 # Hz, 5 samples per second
    T = 1.0/Fs # Sampling Period (Seconds)
    time_vec = numpy.linspace(0.0, N*T, N)
    # Compute FFT
    data_f = scipy.fftpack.fft(data)
    # Define frequency domain of single sided spectrum
    xf = numpy.linspace(0.0, 1.0 / (2.0 * T), N / 2)
    # Plot
    fig, ax = plt.subplots()
    ax.plot(xf, 2.0/N * numpy.abs(data_f[:N//2]))
    ax.set_title(title_str)
    
    


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

# Plotting FFTs of wind speed data

# Select region where we're in trim (hover)
fig4, ax4 = plt.subplots()
ax4.plot(range(len(wind_speed)), wind_speed)
ax4.set_title("Wind Speed with Indices")
# Two sets of trim data
t1 = 0
t2 = 200
t3 = 5500
t4 = 6500

trim_set_1 = wind_speed[t1:t2]
trim_set2 = wind_speed[t3:t4]

plot_fft(trim_set_1, time_stamps[t1:t2], "Wind Speed Trim Set 1 FFT")
plot_fft(trim_set2, time_stamps[t3:t4], "Wind Speed Trim Set 2 FFT")
plot_fft(wind_speed, time_stamps, "Wind Speed FFT")

plt.show()