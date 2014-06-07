from django.contrib import admin
from ATMSpotApp.models import Cluster
from ATMSpotApp.models import ATM
from ATMSpotApp.models import Reason

# Register your models here.
admin.site.register(Cluster, admin.ModelAdmin)
admin.site.register(ATM, admin.ModelAdmin)
admin.site.register(Reason, admin.ModelAdmin)