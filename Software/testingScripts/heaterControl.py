import smbus2
import bme280
import math
import RPi.GPIO as g

from time import sleep

#BME 280 bus/port definition
port = 1
bus = smbus2.SMBus(port)
bmeAddress= 0x76

#BME 280 calibration parameters
calibrationParameters = bme280.load_calibration_params(bus, bmeAddress)

#Initialisation of GPIO pins
g.setmode(g.BOARD)
g.setup(21, g.OUT)


#ZAŠTO JA NEMREM KORISTITI GLOBALNE VARIJABLE OVAKO? koji haos.......
#airTemperature = bme280.sample(bus, bmeAddress, calibrationParameters).temperature
#relativeHumidity = bme280.sample(bus, bmeAddress, calibrationParameters).humidity
#airPressure = bme280.sample(bus, bmeAddress, calibrationParameters).pressure

def getDewPoint(airTemperature, relativeHumidity):
    """Compute the dew point in degrees Celsius
    :param airTemperature: current ambient temperature in degrees Celsius
    :type airTemperature: float

    :param relativeHumidity: relative humidity in %
    :type relativeHumidity: float

    :return: the dew point in degrees Celsius
    :rtype: float
    """
    A = 17.625
    B = 243.04

    alpha = ((A * airTemperature) / (B + airTemperature)) + math.log(relativeHumidity/100.0)
    return (B * alpha) / (A - alpha)

'''
example code for heater
g.output(21, 0)
	print("heater on")
	sleep(300)
	g.output(21, 1)
	g.cleanup()
	print("heater off")
'''

while True:
    sleep(1)

    print("BME 280")
    bmeData = bme280.sample(bus, bmeAddress, calibrationParameters)

    airTemperature = bmeData.temperature
    relativeHumidity = bmeData.humidity
    airPressure = bmeData.pressure

    print(airTemperature)
    print(airPressure)
    print(relativeHumidity)

    print("Dew point is")
    print(getDewPoint(airTemperature, relativeHumidity))
    
    print("==============================")
    print("\033[F"*7, end='')
