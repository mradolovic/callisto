import astropy.units as u
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, Angle
from astropy.time import Time
from datetime import datetime
import RPi.GPIO as g
from constants import SLEEP_TIME
import time

# States a stepper motor can be in row --> state; column --> coil nr.
states = [
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1]
]

# Stepper control initialization
# pins of the 2 motors, 4 coils each
#motors[0] = motor A; motors[1] = motor B
motors = [[15, 13, 12, 11],
          [32, 33, 29, 31]]

g.setmode(g.BOARD)

# IMPORTANT:
# When PCB is printed the motor assignment is as follows:
# motors = [[12, 15, 11, 13], 
#           [31, 33, 32, 29]]

absoluteStepperState = [330000, 330000]

def convertToEquatorial(alt, az):
    '''
    converts alt az coordinates to equatorial
    location: Visnjan
    default alt az for home(?): 30, 180
    returns equatorial coordinates in degrees
    '''
    # defining home pointing in alt az coordinates
    homeAlt = Angle(alt, unit = u.deg)
    homeAz = Angle(az, unit = u.deg)
    home = AltAz(alt = homeAlt, az = homeAz)
    
    # defining location
    loc = EarthLocation(lat = 45.275840*u.deg, lon = 13.721654*u.deg, height = 226*u.m)

    # defining the time
    now = datetime.now()
    time = Time(now, scale='utc', location=loc)

    # defining skycoords object with altaz coordinates and converting home pointing to equatorial
    coords = SkyCoord(alt = home.alt, az = home.az, obstime = now, frame='altaz', location = loc)
    coordseq = coords.transform_to('icrs')
    ra = Angle(coordseq.ra, unit = u.deg)
    #ha = ra.hour_angle(time.sidereal_time('apparent', loc))
    #ha = kutevi.RA.hour_angle(time.sidereal_time('apparent', loc))
    
    return (coordseq.ra.deg, coordseq.dec.deg)

def cleanup(motors):
    '''
    sets all outputs to the motors to 0 (LOW)
    This is done for example to prevent motors from pulling unnecessarily high current when stationary. The used high transmission ratio is enough to hold the steppers in place in most cases.
    '''
    g.output(motors[0][3], 0)
    g.output(motors[0][2], 0)
    g.output(motors[0][1], 0)
    g.output(motors[0][0], 0)
    g.output(motors[1][3], 0)
    g.output(motors[1][2], 0)
    g.output(motors[1][1], 0)
    g.output(motors[1][0], 0)

def moveStepper(motor, steps, dir, absoluteStepperState):
    '''
    moves a stepper a given amount of steps in a given direction
    motor: 0 = ra, 1 = dec
    steps: int number of steps
    dir: -1 = east/north, 1 = west/south
    absoluteStepperState: 
    '''
    
    for i in range(abs(steps)):
        g.output(motors[motor][3], states[absoluteStepperState[motor]%4][0])
        g.output(motors[motor][2], states[absoluteStepperState[motor]%4][1])
        g.output(motors[motor][1], states[absoluteStepperState[motor]%4][2])
        g.output(motors[motor][0], states[absoluteStepperState[motor]%4][3])
        time.sleep(SLEEP_TIME)
        cleanup(motors)
        absoluteStepperState[motor] += dir
    return absoluteStepperState
    
    '''
    sends according signal to pins which control the arduino
    '''
    # g.output(arduinoEnable, 1)
    # ser.write(bytes(f'{steps*dir}\n'))
    # g.output(arduinoEnable, 0)
    
def initMotors():
    '''
    initializes all control pins from the motors list
    '''
    g.setup(motors[0][0], g.OUT)
    g.setup(motors[0][1], g.OUT)
    g.setup(motors[0][2], g.OUT)
    g.setup(motors[0][3], g.OUT)
    g.setup(motors[1][0], g.OUT)
    g.setup(motors[1][1], g.OUT)
    g.setup(motors[1][2], g.OUT)
    g.setup(motors[1][3], g.OUT)
    
def optoCheck():
    '''
    prints opto-interrupter output
    '''
    g.setmode(g.BOARD)
    g.setwarnings(False)
    g.setup(38, g.IN)

    try:
        while True:
            print(g.input(38))
    except KeyboardInterrupt:
        return    
