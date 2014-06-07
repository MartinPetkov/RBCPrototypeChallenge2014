### algorithm to build clusters using disjoint-set data structure

# import ATMs; assume they have some position coordinate property

eps = 0.5 # threshold value; make editable, maybe?

def dist(a_lat, a_lon,b_lat, b_lon):
	'''Return distance between a and b, where a and b are tuples of two points'''
	return sqrt((a_lon-b_lon)**2 + (a_lat-b_lat)**2)

# relevant classes (for reference)

# class Cluster(models.Model):
# 	cluster_id = models.AutoField(primary_key=True, unique=True)
# 	midpoint_lat = models.IntegerField()
# 	midpoint_lon = models.IntegerField()
# 	score = models.IntegerField()

# class ATM(models.Model):
# 	atm_id = models.AutoField(primary_key=True, unique=True)
# 	owner = models.CharField(max_length=50)
# 	address = models.CharField(max_length=50)
# 	lat = models.IntegerField()
# 	lon = models.IntegerField()
# 	trans_per_month = models.IntegerField();
# 	surcharge_type = models.CharField(max_length=10)
# 	average_surchage = models.CharField(max_length=50)
# 	cluster_id = models.ForeignKey(Cluster)

# group ATMs into cluster based on chosen parameter
for i in atm_list:
	for j in atm_list:
		# check that the ATM is within a given neighbourhood
		if dist(i.lat, i.lon, j.lat, j.lon) < eps
			# if it is, add latitude and longitude to midpoint values (will average out later)
			i.cluster_id.midpoint_lat += j.cluster_id.midpoint_lat
			i.cluster_id.midpoint_lon += j.cluster_id.midpoint_lon
			# new score is total of first two scores
			i.cluster_id.score += j.cluster_id.score
			# i and j have same cluster now
			j.cluster_id = i.cluster_id

# populate a list of clusters
cluster_list = []

for i in atm_list:
	if i.cluster_id not in cluster_list:
		cluster_list.append(i.cluster)

# calculate midpoints of each cluster in the list
for cluster in cluster_list:
	# sum over all coordinates
	num_atms = 0
	for atm in atm_list:
		if atm.cluster_id = cluster.cluster_id:
			num_atms += 1
	# divide by total number of atms to obtain average
	cluster.midpoint_lat, cluster.midpoint_lon = cluster.midpoint_lat/num_atms, cluster.midpoint_lon/num_atms

