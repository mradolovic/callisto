from ina219 import INA219
from time import sleep

SHUNT_OHMS = 0.1


MAX_EXPECTED_AMPS_HEATER = 3
MAX_EXPECTED_AMPS_CALLISTO = 0.3
MAX_EXPECTED_AMPS_LNA = 0.05

callistoAddress = 0x44
heaterAddress = 0x42
lnaAddress = 0x40

inaCallisto = INA219(SHUNT_OHMS, busnum=1, address=callistoAddress, max_expected_amps=MAX_EXPECTED_AMPS_CALLISTO)
inaCallisto.configure(inaCallisto.RANGE_16V)

inaHeater = INA219(SHUNT_OHMS, busnum=1, address=heaterAddress, max_expected_amps=MAX_EXPECTED_AMPS_HEATER)
inaHeater.configure(inaHeater.RANGE_32V)

inaLNA = INA219(SHUNT_OHMS, busnum=1, address=lnaAddress, max_expected_amps=MAX_EXPECTED_AMPS_LNA)
inaLNA.configure(inaLNA.RANGE_16V, bus_adc=inaLNA.ADC_128SAMP, gain=inaLNA.GAIN_1_40MV)



def read(ina, inaAddress):
    try:
        print(f"Address: {hex(inaAddress)}")
	#1.02 IS A CORRECTION COEFFICIENT FOUND BY COMPARING INA 
	#AND A KNOWN MULTIMETER
        print(f"Bus Voltage {round(ina.voltage(), 3)}V")
        print(f"Bus Current {round(ina.current()*1.02, 3)}mA")
        print(f"Bus Power {round(ina.power(), 3)}mW")
        print("==============================")
    except DeviceRangeError as e:
        print("Current overflow")

while True:
    sleep(1)
    print("CALLISTO")
    read(inaCallisto, callistoAddress)
    print("LNA")
    read(inaLNA, lnaAddress)
    print("Heater")
    read(inaHeater, heaterAddress)
    print("\033[F"*18, end='')
