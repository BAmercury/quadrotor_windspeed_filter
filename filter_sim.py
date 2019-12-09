# Python 2.7
import numpy
from scipy import signal


"""
    Program that simulates real-time data through a function that will remove
    a user defined DC bias and then filter it
"""


class AirspeedFilter:

    # Constructor
    def __init__(self, sim_duration, filter_order, dc_bias):
        self.sim_duration = sim_duration
        self.filter_order = filter_order
        self.dc_bias = dc_bias
    

    # Construct the filter
    def design_filter(self):
        print("Filter has been initialized")

    # Run the simulation
    def run_sim(self, data, timestamps):
        print("Hello World")




filtobj = AirspeedFilter(10, 2, 5)
filtobj.design_filter()
filtobj.run_sim(1, 1)