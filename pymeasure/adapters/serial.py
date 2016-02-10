#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2016 Colin Jermain, Graham Rowlands
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from .adapter import Adapter

import serial
import numpy as np


class SerialAdapter(Adapter):
    """ Adapter class for using the Python Serial package to allow
    serial communication to instrument

    :param port: Serial port
    :param kwargs: Any valid key-word argument for serial.Serial
    """

    def __init__(self, port, **kwargs):
        self.connection = serial.Serial(port, **kwargs)

    def __del__(self):
        """ Ensures the connection is closed upon deletion
        """
        self.connection.close()

    def write(self, command):
        """ Writes a command to the instrument

        :param command: SCPI command string to be sent to the instrument
        """
        self.connection.write(command.encode()) # encode added for Python 3

    def read(self):
        """ Reads until the buffer is empty and returns the resulting
        ASCII respone

        :returns: String ASCII response of the instrument.
        """
        return b"\n".join(self.connection.readlines()).decode()

    def values(self, command):
        """ Writes a command to the instrument and returns a list of formatted
        values from the result 

        :param command: SCPI command to be sent to the instrument
        :returns: String ASCII response of the instrument
        """
        results = str(self.ask(command)).strip()
        results = results.split(',')
        for result in results:
            try:
                result = float(result)
            except:
                pass # Keep as string
        return results

    def binary_values(self, command, header_bytes=0, dtype=np.float32):
        """ Returns a numpy array from a query for binary data 

        :param command: SCPI command to be sent to the instrument
        :param header_bytes: Integer number of bytes to ignore in header
        :param dtype: The NumPy data type to format the values with
        :returns: NumPy array of values
        """
        self.connection.write(command)
        binary = self.connection.read()
        header, data = binary[:header_bytes], binary[header_bytes:]
        return np.fromstring(data, dtype=dtype)

    def __repr__(self):
        return "<SerialAdapter(port='%s')>" % self.connection.port