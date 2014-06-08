# scoring algorithm

# parameters: 
## transactions per month
## surcharge type
## average surcharge
## owner

# put each cluster's score into cluster.score
#atm_list = ATM.objects.all()
#cluster_list = list(Cluster.objects.all())

# dummy class code for testing!
class ATM():
	owner = ''
	address = ''
	lat = 0.
	lon = 0.
	trans_per_month = 0
	surcharge_type = ''
	average_surcharge = 0.
	cluster_id = None

class Cluster():
	midpoint_lat = 0.
	midpoint_lon = 0.
	score = 0.

# calculate surcharge per month
def calc_monthly_surcharge(atm):
	return atm.trans_per_month * atm.average_surchage

# calculate number of RBC ATMs per cluster
def calc_num_RBC_cluster(cluster):
	# really bad efficiency method assuming that we don't have a mapping from
	# clusters to elements
	count = 0
	for atm in atm_list:
		if atm.cluster_id == cluster.cluster_id and atm.owner == RBC:
			count += 1
	return count

# calculate number of non-RBC atms per cluster
def calc_num_non_RBC_cluster(cluster):
	count = 0
	for atm in atm_list:
		if atm.cluster_id == cluster.cluster_id and atm.owner != RBC:
			count += 1
	return count

# weight: todo: adjust depending on other values?
surcharge_weight = 1.0
rbc_weight = 1.0
non_RBC_weight = 1.0

for cluster in cluster_list:
	sur_tot = 0
	for atm in cluster:
		sur_tot += calc_monthly_surcharge(atm)
	cluster.score = (sur_tot * surcharge_weight - 
					 calc_num_rbc_cluster(cluster) * rbc_weight + 
					 calc_num_non_RBC_cluster(cluster) * non_RBC_weight)



