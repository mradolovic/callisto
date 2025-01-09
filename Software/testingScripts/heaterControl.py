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

'''
example code for heater
g.output(21, 0)
	print("heater on")
	sleep(300)
	g.output(21, 1)
	g.cleanup()
	print("heater off")
'''


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


while True:
    sleep(1)

    print("BME 280")
    #sampling the sensor
    bmeData = bme280.sample(bus, bmeAddress, calibrationParameters)

    #extracting the parameters
    airTemperature = bmeData.temperature
    relativeHumidity = bmeData.humidity
    airPressure = bmeData.pressure

    print(airTemperature)
    print(airPressure)
    print(relativeHumidity)

    #calculating the dew point using RH and temp
    print("Dew point is")
    print(getDewPoint(airTemperature, relativeHumidity))
    
    print("==============================")
    print("\033[F"*7, end='')
