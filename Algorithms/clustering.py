### algorithm to build clusters using disjoint-set data structure



# import ATMs; assume they have some position coordinate property

eps = 0.5 # threshold value; make editable, maybe?

def dist(a_lon, a_lat,b_lon, b_lat):
	'''Return distance between a and b, where a and b are tuples of two points'''
	return sqrt((a_lon-b_lon)**2 + (a_lat-b_lat)**2)

# dummy class to show what's expected from an atm
class atm():
	lat = 0.0
	lon = 0.0
	
class cluster():
	# total lat and long are meaningless in themselves; used with length to calculate midpoint
	atms = []
	mid = [0.0,0.0]

# populate atm_list with clusters
for i in atm_list:
	i.cluster = cluster(i.lat, i.lon, 1)

for i in atm_list:
	for j in atm_list:
		# assuming that the ATMs are classes with parameters lon and lat (longitude & latitude)
		if dist(i.lon, i.lat, j.lon, j.lat) < eps:
			i.cluster.atms.extend(j.cluster.atms)
			j.cluster = i.cluster

# populate a list of clusters
cluster_list = []

for i in atm_list:
	if i.cluster not in cluster_list:
		cluster_list.append(i.cluster)

# calculate midpoints of each cluster in the list
for cluster in cluster_list:
	# sum over all coordinates
	for atm in cluster.atms:
		mid[0], mid[1] += atm.lat, atm.lon
	# calculate average of coordinates to give midpoint
	mid[0] = mid[0]/len(cluster.atms)
	mid[1] = mid[1]/len(cluster.atms)



