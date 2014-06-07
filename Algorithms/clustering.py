### algorithm to build clusters

# import ATMs; assume they have some position coordinate property

eps = 0.5 # threshold value; make editable, maybe?

def dist(a_lon, a_lat,b_lon, b_lat):
	'''Return distance between a and b, where a and b are tuples of two points'''
	return sqrt((a_lon-b_lon)**2 + (a_lat-b_lat)**2)

for i in atm_list:
	for j in atm_list:
		# assuming that the ATMs are classes with parameters lon and lat (longitude & latitude)
		if dist(i.lon, i.lat, j.lon, j.lat) < eps:
			# ATMs should have a cluster id, denoting which cluster they belong to 
			#(by default all belong to separate clusters)
			# set these to be the same
			j.cluster = i.cluster



