# ds18b20.py
# written by Roger Woollett

import os
import glob
import time


class DS18B20:
    # much of this code is lifted from Adafruit web site
    # This class can be used to access one or more DS18B20 temperature sensors
    # It uses OS supplied drivers and one wire support must be enabled
    # To do this add the line
    # dtoverlay=w1-gpio
    # to the end of /boot/config.txt
    #
    # The DS18B20 has three pins, looking at the flat side with the pins pointing
    # down pin 1 is on the left
    # connect pin 1 to GPIO ground
    # connect pin 2 to GPIO 4 *and* GPIO 3.3V via a 4k8 (4800 ohm) pullup resistor
    # connect pin 3 to GPIO 3.3V
    # You can connect more than one sensor to the same set of pins
    # Only one pullup resistor is required

    def __init__(self):
        # Load required kernel modules
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')

        # Find file names for the sensor(s)
        base_dir = '/sys/bus/w1/devices/'
        device_folder = glob.glob(base_dir + '28*')
        self._num_devices = len(device_folder)
        self._device_file = list()
        i = 0
        while i < self._num_devices:
            self._device_file.append(device_folder[i] + '/w1_slave')
            i += 1


    def _read_temp(self, index):
        # Issue one read to one sensor
        # You should not call this directly

        # First check if this index exists
        if index >= len(self._device_file):
            return False

        f = open(self._device_file[index], 'r')
        data = f.read()
        f.close()
        return data


    def tempC(self, index=0):
        # Call this to get the temperature in degrees C
        # detected by a sensor
        data = self._read_temp(index)
        retries = 5

        # Check for error
        if data == False:
            return None

        while (not "YES" in data) and (retries > 0):
            # Read failed so try again
            time.sleep(0.1)
            #print('Read Failed', retries)
            data = self._read_temp(index)
            retries -= 1

        if retries == 0:
            return None

        (discard, sep, reading) = data.partition(' t=')

        if reading == 85000:
            # 85ºC is the boot temperature of the sensor, so ignore that value
            return None

        temperature = float(reading) / 1000.0

        return temperature


    def device_count(self):
        # Call this to see how many sensors have been detected
        return self._num_devices