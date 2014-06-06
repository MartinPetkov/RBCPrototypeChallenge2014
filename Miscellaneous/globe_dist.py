### DISTANCE CALCULATOR given longitude and latitude of two points in sexagesimal

from numpy import *

R = 6367.4447 # radius of Earth in km (changing the units of this changes the
# units of the final distance measurement)

def hsin(x):
    # haversine function; takes argument in radians
    return sin(x/2)**2

def l_to_r(x):
    # convert latitude from sexagesimal to radians because what is sexagesimal even
    return (x[0] + (x[1]/60) + (x[2]/3600))*pi/180.0

# p1 and p2 are tuples (latitude, longitude), with latitude and longitude as tuples of 
# (degrees, minutes, seconds) 
def dist(p1, p2):
    '''
    Return the distance in km between two points on the globe given latitude
    and longitude in degrees, minutes, and seconds'''
    # convert angles to radians
    lat1, lat2, lon1, lon2 = l_to_r(p1[0]), l_to_r(p2[0]), l_to_r(p1[1]), l_to_r(p2[1])
    # haversine formula for distance
    return 2*R*arcsin(sqrt(hsin(lat2-lat1)+cos(lat1)*cos(lat2)*hsin(lon2-lon1)))
