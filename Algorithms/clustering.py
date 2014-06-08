### algorithm to build clusters using disjoint-set data structure

from ATMSpotApp.models import Cluster
from ATMSpotApp.models import ATM

# require all ATM objects from database (syntax?)
atm_list = list(ATM.objects.all())

eps = 0.5 # distance threshold value; make editable, maybe?

def dist(a_lat, a_lon,b_lat, b_lon):
	return sqrt((a_lon-b_lon)**2 + (a_lat-b_lat)**2)

length = len(atm_list)
for i in range(length - 1):
	atm = atm_list[i]
	if not atm.cluster_id:
		c = Cluster(midpoint_lat=0, midpoint_lon=0, score=0)
		c.save()
		atm.cluster_id = c
	
	for j in range(i+1, length):
		# check that the ATM is within a given neighbourhood
		other_atm = atm_list[j]
		if not other_atm.cluster_id:
			if dist(atm.lat, atm.lon, other_atm.lat, other_atm.lon) < eps:
				# update the atm's cluster ID in database
				other_atm.cluster_id = atm.cluster_id
				other_atm.save()

# this is a list of all the final clusters; may want to throw in database
cluster_list = Cluster.objects.all()

for cluster in cluster_list:
	atms_for_cluster = ATM.objects.filter(cluster_id_id=cluster.cluster_id)
	num_atms = atms_for_cluster.count()
	
	sum_lat = 0
	for a in atms_for_cluster:
		sum_lat += a.lat

	sum_lon = 0
	for a in atms_for_cluster:
		sum_lon += a.lon

	# update cluster midpoint values in database
	cluster.midpoint_lat, cluster.midpoint_lon = sum_lat/num_atms, sum_lon/num_atms

	cluster.save()
