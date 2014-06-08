from django.db import models

# Create your models here.
class Cluster(models.Model):
	cluster_id = models.AutoField(primary_key=True, unique=True)
	midpoint_lat = models.FloatField()
	midpoint_lon = models.FloatField()
	score = models.IntegerField()

	def __str__(self):
		return "[Midpoint: (%s, %s) | Score: %s]" % (self.midpoint_lat, self.midpoint_lon, self.score)

	class Admin:
		pass


class ATM(models.Model):
	SURCHARGE_TYPES = (
		('N', 'None'),
		('F', 'Flat'),
		('R', 'Rate'),
	)
	atm_id = models.AutoField(primary_key=True, unique=True)
	owner = models.CharField(max_length=50)
	address = models.CharField(max_length=50)
	lat = models.FloatField()
	lon = models.FloatField()
	trans_per_month = models.IntegerField();
	surcharge_type = models.CharField(max_length=10, choices=SURCHARGE_TYPES)
	average_surcharge = models.FloatField()
	cluster_id = models.ForeignKey(Cluster, null=True)

	def __str__(self):
		return "[Owner: %s | Address: %s | Coordinates: (%s, %s) | Montly Transactions: %s | Surcharge: %s, %f | Cluster: %s]" % (self.owner, self.address, self.lat, self.lon, self.trans_per_month, self.surcharge_type, self.average_surcharge, self.cluster_id)

	class Admin:
		pass


class Reason(models.Model):
	ALIGNMENTS = (
		('G', 'Good'),
		('B', 'Bad')
		)
	reason_id = models.AutoField(primary_key=True, unique=True)
	alignment = models.CharField(max_length=50, choices=ALIGNMENTS)
	reason_text = models.CharField(max_length=50)
	cluster_id = models.ForeignKey(Cluster)

	def __str__(self):
		return "[Alignment: %s | Details: %s | Cluster: %s]" % (self.alignment, self.reason_text, self.cluster_id)

	class Admin:
		pass