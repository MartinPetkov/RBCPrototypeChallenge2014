### DISTANCE CALCULATOR given longitude and latitude of two points in sexagesimal

from numpy import sin, arcsin, pi, cos, sqrt

R = 6367.4447 # radius of Earth in km (changing the units of this changes the
# units of the final distance measurement)

def hsin(x):
    # haversine function; takes argument in radians
    return sin(x/2)**2

def l_to_r(x):
    # convert latitude from deg to rad
    return pi/180.0

def dist(a_lat, a_lon, b_lat, b_lon):
    # convert angles to radians
    lat1, lat2, lon1, lon2 = l_to_r(a_lat), l_to_r(b_lat), l_to_r(a_lon), l_to_r(b_lon)
    # haversine formula for distance
    return 2*R*arcsin(sqrt(hsin(lat2-lat1)+cos(lat1)*cos(lat2)*hsin(lon2-lon1)))
