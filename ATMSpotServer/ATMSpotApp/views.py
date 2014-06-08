from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
import json
from ATMSpotApp.models import Cluster
from ATMSpotApp.models import ATM
from django.db.models.query import QuerySet
from matplotlib.path import Path
import pdb
from django.views.decorators.csrf import csrf_exempt
import csv
from numpy import sin, arcsin, pi, cos, sqrt
import random

R = 6367.4447 # radius of Earth in km (changing the units of this changes the
BAD_REASONS = {
	"monthly_surcharge_low": "- Too few people paying surcharges on non-<a href='http://www.rbc.com/caribbean.html'>RBC</a> ATMs in this area",
	"total_num_rbc_high": "- Large number of <a href='http://www.rbc.com/caribbean.html'>RBC</a> ATMs in this area",
	"non_rbc_low": "- Too few non-<a href='http://www.rbc.com/caribbean.html'>RBC</a> ATMs in the area",
	"trans_rbc_low": "- Too few <a href='http://www.rbc.com/caribbean.html'>RBC</a> transactions from <a href='http://www.rbc.com/caribbean.html'>RBC</a> ATMs in this area",
	"trans_non_rbc_low": "- Too few transactions from <a href='http://www.rbc.com/caribbean.html'>RBC</a> customers through non-RBC ATMs in this area",
}

GOOD_REASONS = {
	"monthly_surcharge_high": "+ Many people paying surcharges on non-RBC ATMs in this area",
	"total_num_rbc_low": "+ Low number of RBC ATMs in this area",
	"non_rbc_high": "+ Many non-RBC ATMs in the area",
	"trans_rbc_high": "+ Many RBC transactions from RBC ATMs in this area",
	"trans_non_rbc_high": "+ Many transactions from RBC customers through non-RBC ATMs in this area",
}


# Create your views here.
def homepage(request):
	# Return the homepage
	return render_to_response("homepage.html")

@csrf_exempt
def clusters_in_box(request):
	# Return the clusters info as a JSON response

	clusters = {}

	# Select clusters whose midpoints fall within the give coordinates
	db_cluster_list = Cluster.objects.all()

	coordinates = json.loads(request.body)
	#pdb.set_trace()
	new_cluster_list = filter_db_cluster_list(db_cluster_list, coordinates)
	cluster_list = []

	if(new_cluster_list):
		for cluster in new_cluster_list:
			one_cluster = {}

			atms_for_cluster = ATM.objects.filter(cluster_id_id=cluster.cluster_id)
			reasons_for_cluster = calculate_score(request, cluster)

			one_cluster["cluster_id"] = cluster.cluster_id
			one_cluster["midpoint_lat"] = cluster.midpoint_lat
			one_cluster["midpoint_lon"] = cluster.midpoint_lon
			one_cluster["score"] = cluster.score

			atms_list = []
			reasons_list = []
			# Put all the ATM info into one_cluster
			for atm in atms_for_cluster:
				one_atm = {}
				one_atm["atm_id"] = atm.atm_id
				one_atm["owner"] = atm.owner
				one_atm["address"] = atm.address
				one_atm["lat"] = atm.lat
				one_atm["lon"] = atm.lon
				one_atm["trans_per_month"] = atm.trans_per_month
				one_atm["surcharge_type"] = atm.surcharge_type
				one_atm["average_surcharge"] = atm.average_surcharge

				atms_list.append(one_atm)

			# Put all the Reason info into one_cluster
			for reason in reasons_for_cluster:
				one_reason = {}
				one_reason["alignment"] = reason.get('alignment')
				one_reason["reason_text"] = reason.get('reason_text')

				reasons_list.append(one_reason)

			one_cluster["ATMs"] = atms_list
			one_cluster["Reasons"] = reasons_list
			cluster_list.append(one_cluster)


	clusters["clusters"] = cluster_list
	response = HttpResponse(json.dumps(clusters), content_type="application/json")
	response['Access-Control-Allow-Origin'] = '*'
	response['X-Frame-Options'] = ''
	return response

def populate_db(request):
	path_prefix = "../DataScraping/ATMs_in_brampton/"
	populateDB("RBC", path_prefix + "RBC/positions.csv")
	populateDB("CIBC", path_prefix + "CIBC/positions.csv")
	populateDB("BMO", path_prefix + "BMO/positions.csv")
	populateDB("Scotia", path_prefix + "Scotia/positions.csv")
	populateDB("TD", path_prefix + "TD/positions.csv")

	return HttpResponse("DB has been populated")

def calculate_clusters(request):
	# require all ATM objects from database (syntax?)
	atm_list = list(ATM.objects.all())

	eps = 0.3 # distance threshold value; make editable, maybe?

	length = len(atm_list)
	for i in range(length):
		atm = atm_list[i]
		if not atm.cluster_id:
			c = Cluster(midpoint_lat=0, midpoint_lon=0, score=0)
			c.save()
			atm.cluster_id = c
			atm.save()
		
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
		
		if num_atms > 0:
			sum_lat = 0
			for a in atms_for_cluster:
				sum_lat += a.lat

			sum_lon = 0
			for a in atms_for_cluster:
				sum_lon += a.lon

			# update cluster midpoint values in database
			cluster.midpoint_lat, cluster.midpoint_lon = sum_lat/num_atms, sum_lon/num_atms

		cluster.save()

	return HttpResponse("Clusters have been calculated")

def calculate_score(request, cluster):
	# weight: todo: adjust depending on other values?
	surcharge_weight = 1.0
	RBC_trans_w = 1.0
	non_RBC_trans_w = 1.0
	num_ratio_w = 1.0

	# Add default values if not set
	thresholds = json.loads(request.body)
	if thresholds.get("w_surt_tot"):
		w_sur_tot_low = thresholds.get("w_surt_tot").get("low")
		w_sur_tot_high = thresholds.get("w_surt_tot").get("high")
	else:
		w_sur_tot_low = 100.
		w_sur_tot_high = 1000.

	if thresholds.get("tot_num_RBC"):
		tot_num_RBC_low = thresholds.get("tot_num_RBC").get("low")
		tot_num_RBC_high = thresholds.get("tot_num_RBC").get("high")
	else:
		tot_num_RBC_low = 1 # Default
		tot_num_RBC_high = 4 # Default

	if thresholds.get("w_trans_RBC"):
		w_trans_RBC_low = thresholds.get("w_trans_RBC").get("low")
		w_trans_RBC_high = thresholds.get("w_trans_RBC").get("high")
	else:
		w_trans_RBC_low = 20 # Default
		w_trans_RBC_high = 200 # Default

	if thresholds.get("tot_num_non_RBC"):
		tot_num_non_RBC_low = thresholds.get("tot_num_non_RBC").get("low")
		tot_num_non_RBC_high = thresholds.get("tot_num_non_RBC").get("high")
	else:
		tot_num_non_RBC_low = 1 # Default
		tot_num_non_RBC_high = 4 # Default

	if thresholds.get("w_trans_non_RBC"):
		w_trans_non_RBC_low = thresholds.get("w_trans_non_RBC").get("low")
		w_trans_non_RBC_high = thresholds.get("w_trans_non_RBC").get("high")
	else:
		w_trans_non_RBC_low = 20 # Default
		w_trans_non_RBC_high = 200 # Default

	reasons = []

	# score for cluster: combination of weighted surcharge total, 
	# minus weighted number of transactions on RBC machines,
	# plus weighted number of transactions on other bank machines,
	# multiplied by the weighted ratio of non-RBC machines to RBC machines
	w_sur_tot = calc_monthly_surcharge(cluster) * surcharge_weight
	# Update reasons if needed
	if w_sur_tot <= w_sur_tot_low:
		# Create bad reason for monthly_surcharge_low
		reasons.append({"alignment": 'B', "reason_text": BAD_REASONS.get('monthly_surcharge_low')})
	elif w_sur_tot >= w_sur_tot_high:
		# Create good reason for monthly_surcharge_high
		reasons.append({"alignment": 'G', "reason_text": GOOD_REASONS.get('monthly_surcharge_high')})

	tot_num_RBC, w_trans_RBC = calc_RBC(cluster)
	# Update reasons if needed
	if tot_num_RBC <= tot_num_RBC_low:
		# Create good reason for total_num_rbc_low
		reasons.append({"alignment": 'G', "reason_text": GOOD_REASONS.get('total_num_rbc_low')})
	elif tot_num_RBC >= tot_num_RBC_high:
		# Create bad reason for total_num_rbc_high
		reasons.append({"alignment": 'B', "reason_text": BAD_REASONS.get('total_num_rbc_high')})

	w_trans_RBC *= RBC_trans_w
	# Update reasons if needed
	if w_trans_RBC <= w_trans_RBC_low:
		# Create bad reason for trans_rbc_low
		reasons.append({"alignment": 'B', "reason_text": BAD_REASONS.get('trans_rbc_low')})
	elif w_trans_RBC >= w_trans_RBC_high:
		# Create good reason for trans_rbc_high
		reasons.append({"alignment": 'G', "reason_text": GOOD_REASONS.get('trans_rbc_high')})

	tot_num_non_RBC, w_trans_non_RBC = calc_RBC(cluster)
	# Update reasons if needed
	if tot_num_non_RBC <= tot_num_non_RBC_low:
		# Create bad reason for non_rbc_low
		reasons.append({"alignment": 'B', "reason_text": BAD_REASONS.get('non_rbc_low')})
	elif tot_num_non_RBC >= tot_num_non_RBC_high:
		# Create good reason for non_rbc_high
		reasons.append({"alignment": 'G', "reason_text": GOOD_REASONS.get('non_rbc_high')})

	w_trans_non_RBC *= non_RBC_trans_w
	# Update reasons if needed
	if w_trans_non_RBC <= w_trans_non_RBC_low:
		# Create bad reason for trans_non_rbc_low
		reasons.append({"alignment": 'B', "reason_text": BAD_REASONS.get('trans_non_rbc_low')})
	elif w_trans_non_RBC >= w_trans_non_RBC_high:
		# Create good reason for trans_non_rbc_high
		reasons.append({"alignment": 'G', "reason_text": GOOD_REASONS.get('trans_non_rbc_high')})

	tot_num_RBC += 1
	w_num_rat = num_ratio_w * tot_num_non_RBC/tot_num_RBC

	# Higher is better
	cluster.score = (w_num_rat*(w_sur_tot - w_trans_RBC + w_trans_non_RBC))
	cluster.save()

	return reasons



########################################## Helper Methods ######################################################################
def filter_db_cluster_list(db_cluster_list, coordinates):
	nw = coordinates.get("NW")
	ne = coordinates.get("NE")
	sw = coordinates.get("SW")
	se = coordinates.get("SE")

	new_cluster_list = []

	if(nw and ne and sw and se):
		box = Path([(nw.get("lat"), nw.get("lon")), (ne.get("lat"), ne.get("lon")), (sw.get("lat"), sw.get("lon")), (se.get("lat"), se.get("lon"))])

		#pdb.set_trace()

		# Do magic and filter
		for cluster in db_cluster_list:
			midpoint = [cluster.midpoint_lat, cluster.midpoint_lon]
			if(contains_point(box, midpoint)):
				new_cluster_list.append(cluster)

	return new_cluster_list

#def dist(a_lat, a_lon, b_lat, b_lon):
#	return sqrt((a_lon-b_lon)**2 + (_lat-b_lat)**2)

def dist(a_lat, a_lon, b_lat, b_lon):
	# convert angles to radians
	lat1, lat2, lon1, lon2 = l_to_r(a_lat), l_to_r(b_lat), l_to_r(a_lon), l_to_r(b_lon)
	# haversine formula for distance
	return 2*R*arcsin(sqrt(hsin(lat2-lat1)+cos(lat1)*cos(lat2)*hsin(lon2-lon1)))

def hsin(x):
	# haversine function; takes argument in radians
	return sin(x/2)**2

def l_to_r(x):
	# convert latitude from deg to rad
	return x*(pi/180.0)

def contains_point(box, midpoint):
	contains = box.contains_point(midpoint)
	return contains

def populateDB(owner, csvFileName):
	with open(csvFileName, 'r') as csvFile:
		mrReader = csv.reader(csvFile, delimiter = ',', quotechar = '"')
		next(mrReader, None)  # skip the headers
		for row in mrReader:
			if len(row) < 4:
				continue
			p = ATM(
				owner = owner,
				address = row[3],
				lat = row[0],
				lon = row[1],
				trans_per_month = random.randint(10, 1000),
				surcharge_type = 'Flat',
				average_surcharge = ((abs(((random.random() + random.random())/2.0)-0.5))*2) * 3.5 + 1.5, # 1.5-5.0, leaning low
				)
			p.save()

# calculate surcharge per month (for non-RBC ATMs; assume RBC ATMs have no surcharge)
def calc_monthly_surcharge(cluster):
	surcharge = 0.
	atms_list = ATM.objects.filter(cluster_id_id=cluster.cluster_id)
	for atm in atms_list:
		surcharge += atm.trans_per_month * atm.average_surcharge
	return surcharge

# calculate number of RBC ATMs per cluster and their total number of monthly transactions
def calc_RBC(cluster):
	count = 0
	total_trans = 0
	atms_list = ATM.objects.filter(cluster_id_id=cluster.cluster_id)
	for atm in atms_list:
		if atm.owner == 'RBC':
			count += 1
			total_trans += atm.trans_per_month
	return (count, total_trans)

# calculate number of non-RBC atms per cluster and their total number of monthly transactions
def calc_non_RBC(cluster):
	count = 0
	total_trans = 0
	atms_list = ATM.objects.filter(cluster_id_id=cluster.cluster_id)
	for atm in atms_list:
		if atm.owner != 'RBC':
			count += 1
			total_trans += atm.trans_per_month
	return (count, total_trans)