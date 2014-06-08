# scoring algorithm

# parameters: 
## transactions per month
## surcharge type
## average surcharge
## owner

# put each cluster's score into cluster.score
# atm_list = ATM.objects.all()
# cluster_list = list(Cluster.objects.all())

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

# calculate surcharge per month (for non-RBC ATMs; assume RBC ATMs have no surcharge)
def calc_monthly_surcharge(cluster):
	surcharge = 0.
	for atm in cluster:
		surcharge += atm.trans_per_month * atm.average_surchage
	return surcharge

# calculate number of RBC ATMs per cluster and their total number of monthly transactions
def calc_RBC(cluster):
	count = 0
	total_trans = 0
	for atm in atm_list:
		if atm.cluster_id == cluster.cluster_id and atm.owner == 'RBC':
			count += 1
			total_trans += atm.trans_per_month
	return (count, total_trans)

# calculate number of non-RBC atms per cluster and their total number of monthly transactions
def calc_non_RBC(cluster):
	count = 0
	total_trans = 0
	for atm in atm_list:
		if atm.cluster_id == cluster.cluster_id and atm.owner != 'RBC':
			count += 1
			total_trans += atm.trans_per_month
	return (count, total_trans)


# create some values for testing (don't have to be accurate)	
#c1 = Cluster(2,1,0)
#atm1 = ATM('RBC', '15 Front St.', 2.,3.,4,'flat',c1)
#atm2 = ATM('BMO', '15 Front St.', 2.,2.9,6,'flat',c1)

# weight: todo: adjust depending on other values?
surcharge_weight = 1.0
RBC_trans_w = 1.0
non_RBC_trans_w = 1.0
num_ratio_w = 1.0

cluster_list = Cluster.objects.all()
for cluster in cluster_list:
	# score for cluster: combination of weighted surcharge total, 
	# minus weighted number of RBC machines,
	# plus weighted number of other bank machines,
	# multiplied by the weighted ratio of transactions of non-RBC machines to
	# transactions on RBC machines
	w_sur_tot = calc_monthly_surcharge(cluster) * surcharge_weight
	tot_num_RBC, w_trans_RBC = calc_RBC(cluster)
	w_trans_RBC *= RBC_trans_w
	tot_num_non_RBC, w_trans_non_RBC = calc_RBC(cluster)
	w_trans_non_RBC *= non_RBC_trans_w
	w_num_rat = num_ratio_w * tot_num_non_RBC/tot_num_RBC

	cluster.score = (w_num_rat*(w_sur_tot - w_trans_RBC + w_trans_non_RBC))
	cluster.save()



