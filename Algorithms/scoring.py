# scoring algorithm

# parameters: 
## transactions per month
## surcharge type
## average surcharge
## owner

# calculate surcharge per month?

atm_list = ATM.objects.all()
cluster_list = Cluster.objects.all()

def calc_monthly_surcharge(atm):
	return atm.trans_per_month * atm.average_surchage


