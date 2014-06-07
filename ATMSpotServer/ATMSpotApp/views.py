from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
import json
from ATMSpotApp.models import Cluster
from ATMSpotApp.models import ATM
from ATMSpotApp.models import Reason
from django.db.models.query import QuerySet
from matplotlib.path import Path


# Create your views here.
def homepage(request):
	# Return the homepage
	return render_to_response("homepage.html")


def clusters_in_box(request):
	# Return the clusters info as a JSON response
	NW = request.META.get('NW')
	NE = request.META.get('NE')
	SW = request.META.get('SW')
	SE = request.META.get('SE')

	clusters = {}

	# Select clusters whose midpoints fall within the give coordinates
	db_cluster_list = Cluster.objects.all()

	coordinates = {}
	#coordinates["NW"] = NW
	#coordinates["NE"] = NE
	#coordinates["SW"] = SW
	#coordinates["SE"] = SE
	coordinates["NW"] = {"lat": 1, "lon": 1}
	coordinates["NE"] = {"lat": 2, "lon": 2}
	coordinates["SW"] = {"lat": 3, "lon": 3}
	coordinates["SE"] = {"lat": 4, "lon": 4}
	db_cluster_list = filter_db_cluster_list(db_cluster_list, coordinates)
	cluster_list = []

	for cluster in db_cluster_list:
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
			one_atm["average_surchage"] = atm.average_surchage

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
	return HttpResponse(json.dumps(clusters), content_type="application/json")




########################################## Helper Methods ######################################################################
def filter_db_cluster_list(db_cluster_list, coordinates):
	nw = coordinates.get("NW")
	ne = coordinates.get("NE")
	sw = coordinates.get("SW")
	se = coordinates.get("SE")

	new_cluster_list = QuerySet(Cluster)

	# Do magic and filter
	for cluster in db_cluster_list:
		box = Path([[nw.get("lat"), nw.get("lon")], [ne.get("lat"), ne.get("lon")], [sw.get("lat"), sw.get("lon")], [se.get("lat"), se.get("lon")]])

		if(box.contains_point([cluster.midpoint_lat, cluster.midpoint_lon])):
			print "w00t"

	return db_cluster_list