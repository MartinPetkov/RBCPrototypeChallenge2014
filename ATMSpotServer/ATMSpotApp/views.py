from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
import json
from ATMSpotApp.models import Cluster
from ATMSpotApp.models import ATM
from ATMSpotApp.models import Reason
from django.db.models.query import QuerySet
from matplotlib.path import Path
from math import sqrt
import pdb
from django.views.decorators.csrf import csrf_exempt
import csv


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
			reasons_for_cluster = Reason.objects.filter(cluster_id_id=cluster.cluster_id)

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
				one_reason["reason_id"] = reason.reason_id
				one_reason["alignment"] = reason.alignment
				one_reason["reason_text"] = reason.reason_text

				reasons_list.append(one_reason)

			one_cluster["ATMs"] = atms_list
			one_cluster["Reasons"] = reasons_list
			cluster_list.append(one_cluster)


	clusters["clusters"] = cluster_list
	response = HttpResponse(json.dumps(clusters), content_type="application/json")
	response['Access-Control-Allow-Origin'] = '*'
	response['X-Frame-Options'] = ''
	return response

def calculate_clusters(request):
	# require all ATM objects from database (syntax?)
	atm_list = list(ATM.objects.all())

	eps = 0.001 # distance threshold value; make editable, maybe?

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


def populate_db(request):
	path_prefix = "../DataScraping/ATMs_in_brampton/"
	populateDB("RBC", path_prefix + "RBC/positions.csv")
	populateDB("CIBC", path_prefix + "CIBC/positions.csv")
	populateDB("BMO", path_prefix + "BMO/positions.csv")
	populateDB("Scotia", path_prefix + "Scotia/positions.csv")
	populateDB("TD", path_prefix + "TD/positions.csv")

	return HttpResponse("DB Has been populated")


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

def dist(a_lat, a_lon,b_lat, b_lon):
		return sqrt((a_lon-b_lon)**2 + (a_lat-b_lat)**2)

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
				trans_per_month = 10,
				surcharge_type = 'Flat',
				average_surcharge = 1.0,
				)
			p.save()