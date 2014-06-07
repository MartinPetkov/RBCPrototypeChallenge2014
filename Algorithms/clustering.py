### algorithm to build clusters using disjoint-set data structure

# require all ATM objects from database (syntax?)
atm_list = ATM.objects.all()

eps = 0.5 # distance threshold value; make editable, maybe?

def dist(a_lat, a_lon,b_lat, b_lon):
	return sqrt((a_lon-b_lon)**2 + (a_lat-b_lat)**2)

for i in atm_list:
	for j in atm_list:
		# check that the ATM is within a given neighbourhood
		if dist(i.lat, i.lon, j.lat, j.lon) < eps
			# upate ATM cluster IDs in database
			i.cluster_id.midpoint_lat += j.cluster_id.midpoint_lat
			i.cluster_id.midpoint_lon += j.cluster_id.midpoint_lon
			# update cluster ID values in database
			i.cluster_id.score += j.cluster_id.score
			# update the atm's cluster ID in database
			j.cluster_id = i.cluster_id

# this is a list of all the final clusters; may want to throw in database
cluster_list = []
for i in atm_list:
	if i.cluster_id not in cluster_list:
		cluster_list.append(i.cluster)

for cluster in cluster_list:
	num_atms = 0
	for atm in atm_list:
		if atm.cluster_id == cluster.cluster_id:
			num_atms += 1
	# update cluster midpoint values in database
	cluster.midpoint_lat, cluster.midpoint_lon = cluster.midpoint_lat/num_atms, cluster.midpoint_lon/num_atms

