from django.conf.urls import patterns, include, url

from ATMSpotApp.views import homepage
from ATMSpotApp.views import clusters_in_box
from ATMSpotApp.views import calculate_clusters
from ATMSpotApp.views import populate_db

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ATMSpotServer.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^ATMapper/home/$', homepage),
    url(r'^ATMapper/clusters/$', clusters_in_box),
    url(r'^ATMapper/calculate_clusters/$', calculate_clusters),
    url(r'^ATMapper/populate_db/$', populate_db),
)
