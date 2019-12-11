# python 2.7
from matplotlib import pyplot as plt
import scipy.fftpack
from scipy import signal
import numpy
import tkinter as tk
from tkinter import filedialog
import csv
from datetime import datetime
import time

"""
    Program to view and analyze Trinsonica Airspeed sensor logs
"""


# Convert a date-time string into a timestamp in seconds
def fix_timestamp(datetime_str):
    datetime_list = list(datetime_str.split(" "))
    timestamp_str = datetime_list[1]
    h, m, s = timestamp_str.split(':')
    return float(h) * 3600.0 + float(m) * 60.0 + float(s)

# Remove Bias, just subtracts a DC biasc value from every value in the list
def remove_bias(data, dc_bias):
    dc_bias = dc_bias
    data = [item - dc_bias for item in data]
    #data = signal.detrend(data)
    return data


# Plot FFT of given set of data
def plot_fft(data, timestamps, title_str, dc_bias):
    # Remove DC bias from the data (detrend), remove mean
    data = numpy.asarray(data, dtype=numpy.float32)
    data = remove_bias(data, dc_bias)
    # Number of samples
    N = len(data)
    Fs = 5.0 # Hz, 5 samples per second
    T = 1.0/Fs # Sampling Period (Seconds)
    # Compute FFT
    data_f = scipy.fftpack.fft(data)
    # Define frequency domain of single sided spectrum
    xf = numpy.linspace(0.0, 1.0 / (2.0 * T), N / 2)
    # Plot
    fig, ax = plt.subplots()
    ax.plot(xf, 2.0/N * numpy.abs(data_f[:N//2]))
    ax.set_title("FFT: " + title_str)
    
 # Smooth data (Lowpass FIR filter, moving average)
def smooth(data, n=5):
    data = numpy.cumsum(data, dtype=numpy.float32)
    data[n:] = data[n:] - data[:-n]
    return data[n - 1:] / n


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

#fig1, ax1 = plt.subplots()
#ax1.plot(time_stamps, pitch)
#ax1.set_title("Pitch")

#fig2, ax2 = plt.subplots()
#ax2.plot(time_stamps, roll)
#ax2.set_title("Roll")


#fig3, ax3 = plt.subplots()
#ax3.plot(time_stamps, wind_speed)
#ax3.set_title("Wind Speed")




# Plotting FFTs of wind speed data

# Select region where we're in trim (hover, meaning that there should be no airspeed, just windspeed)
fig4, ax4 = plt.subplots()
ax4.plot(range(len(wind_speed)), wind_speed)
ax4.set_title("Raw Air Speed with Indices")
# Indices for the trim data
t1 = 0
t2 = 950

trim_set_1 = wind_speed[t1:t2]
trim_set_1 = numpy.asarray(trim_set_1, dtype=numpy.float32)
print("DC Bias Mean: %f" % numpy.mean(trim_set_1))
# Taking the mean of the data and using that as the DC bias
dc_bias = numpy.mean(trim_set_1)

# Remove DC bias and plot the FFT
plot_fft(wind_speed, time_stamps, "Raw Air Speed", dc_bias)


# Get the ground speed data to compare with
file_path = filedialog.askopenfilename()
print("SSS Log Path: " + file_path)
"""
    Logs will have the following format:
        Time,SSS_GPS_LAT,SSS_GPS_LON,SSS_GPS_ALT,SSS_GPS_VEL_X,SSS_GPS_VEL_Y,SSS_GPS_HEADING,SSS_GPS_GROUNDSPEED,VEHICLE_LAT,VEHICLE_LON,VEHICLE_ALT,
        VEHICLE_ALT_DESIRED,VEHICLE_THROTTLE,VEHICLE_GROUNDSPEED,VEHICLE_DISTANCE_ERROR,
        MOTIONCONTROLLER_SPRING_LENGTH,MOTIONCONTROLLER_TETHER_OUT,
        MOTIONCONTROLLER_DRUM_SPEED,MOTIONCONTROLLER_DANCER_POSITION,VEHICLE_STATE,MOTIONCONTROLLER_STATE,SSS_GPS_STATE,POWERSUPPLY_STATE,COORDINATOR_STATE,
        MavLink Msg Rate,MavLink Unique Msg Rate
"""
sss_time_stamps = []
ground_speed = []

with open(file_path) as datafile:
    csv_reader = csv.reader(datafile, delimiter=',')
    for row in csv_reader:
        datetime_str = row[0]
        sss_time_stamps.append(fix_timestamp(datetime_str))
        ground_speed.append(row[13])

ground_speed = numpy.asarray(ground_speed, dtype=numpy.float32)

# Plot debiased data and ground speed to make sure it matches up
wind_speed_d = numpy.asarray(wind_speed, dtype=numpy.float32)
wind_speed_d = remove_bias(wind_speed_d, dc_bias)
fig5, ax5 = plt.subplots()
ax5.plot(sss_time_stamps, ground_speed, label='Ground Speed')
ax5.plot(time_stamps, wind_speed_d, label='Debiased Airspeed')
ax5.set_title("Ground Speed and Debiased Air Speed")
ax5.legend()

# Calculate Mean Square error between Estimator (Unbiased Airspeed) and the True value (Ground Speed)
# Smaller the MSE value is, the closer our estimated data is to ground truth
mse = numpy.square(numpy.subtract(ground_speed, wind_speed_d[0:len(ground_speed)])).mean()
print("Mean Square Error: %f" % mse)

# Calculate RSME, which is the distance, on average, of a data point from the ground truth line
rsme = numpy.sqrt(mse)
print("Root Mean Square Error: %f" % rsme)
textstr = ("RSME %f" % rsme)
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
ax5.text(0.05, 0.95, textstr, transform=ax5.transAxes, fontsize=11,
    verticalalignment='top', bbox=props)

# Filter Data and check statistics again
# Lowpass FIR Filter (Moving Average Filter)
ma_window = 100
wind_speed_f = smooth(wind_speed_d, ma_window)
fig6, ax6 = plt.subplots()
ax6.plot(sss_time_stamps, ground_speed, label='Ground Speed')
ax6.plot(time_stamps[0:len(wind_speed_f)], wind_speed_f, label='Filt Debiased Airspeed')

ax6.set_title("Ground Speed and Filt Debiased Air Speed")
ax6.legend()
# Calculate statistics
mse = numpy.square(numpy.subtract(ground_speed[0:len(wind_speed_f)], wind_speed_f[0:len(ground_speed)])).mean()
rsme = numpy.sqrt(mse)
textstr = ("RSME: %f" % rsme) + ("\nMA Window: %f" % ma_window)
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
ax6.text(0.05, 0.95, textstr, transform=ax6.transAxes, fontsize=11,
    verticalalignment='top', bbox=props)

plt.show()