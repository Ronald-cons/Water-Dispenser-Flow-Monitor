#coding:Ronald B Liu
##IDE PyCharm Ubuntu 18.04
#Water Flow Monitor: speed dispaly and volume calculation
"""
Plots channels zero and one in two different windows. Requires pyqtgraph.
Read sensor -> Filter -> Plot
"""

import sys
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
from pyfirmata2 import Arduino
import iir_filter_complete


PORT = Arduino.AUTODETECT

# create a global QT application object
app = QtGui.QApplication(sys.argv)

# signals to all threads in endless loops that we'd like to run these
running = True


class QtPanningPlot:

    def __init__(self, title):
        self.win = pg.GraphicsLayoutWidget()
        self.win.setWindowTitle(title)
        self.plt = self.win.addPlot()
        self.plt.setYRange(-1, 1)
        self.plt.setXRange(0, 500)
        self.curve = self.plt.plot()
        self.data = []
        # any additional initalisation code goes here (filters etc)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(100)
        self.layout = QtGui.QGridLayout()
        self.win.setLayout(self.layout)
        self.win.show()

    def update(self):
        self.data = self.data[-500:]
        if self.data:
            self.curve.setData(np.hstack(self.data))

    def addData(self, d):
        self.data.append(d)


# Let's create two instances of plot windows
qtPanningPlot1 = QtPanningPlot("Arduino 1st channel")
qtPanningPlot2 = QtPanningPlot("Arduino 2nd channel")

# sampling rate: 100Hz
samplingRate = 100
count: int = 0
#do filter here-----------------------------------------
myFilter = iir_filter_complete.IIR(2, [1, 8], 'bandpass', design='butter')
# called for every new sample at channel 0 which has arrived from the Arduino
# "data" contains the new sample
def callBack(data):
    # filter your channel 0 samples here:
    # data = self.filter_of_channel0.dofilter(data)
    # send the sample to the plotwindow
    threshold = 0.1
    qtPanningPlot1.addData(data)
    ch1 = board.analog[0].read()
    # 1st sample of 2nd channel might arrive later so need to check
    if ch1:
        # filter your channel 1 samples here:
        ch1 = myFilter.doFilter(ch1)
        qtPanningPlot2.addData(ch1)
        global count
        if (ch1 > threshold):
            #calculate it by experience value 1.79?
            count += 1
        #if count += 1, count -14 to estimate the start up 
        print('Total mL ',count - 14)

        if count > 500:
            print('Stop!Halt!Bitte sparen Sie Ressourcen!')

# Get the Ardunio board.
board = Arduino(PORT)

# Set the sampling rate in the Arduino
board.samplingOn(1000 / samplingRate)

# Register the callback which adds the data to the animated plot
# The function "callback" (see above) is called when data has
# arrived on channel 0.
board.analog[0].register_callback(callBack)

# Enable the callback
board.analog[0].enable_reporting()
board.analog[1].enable_reporting()

# showing all the windows
app.exec_()

# needs to be called to close the serial port
board.exit()

print("Finished")
