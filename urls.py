from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^add_drink/(?P<personid>\d+)/$', 'drinkcounter.views.add_drink'),
    (r'^get_datas/$', 'drinkcounter.views.get_datas'),
    (r'^statistics/$', 'drinkcounter.views.statistics'),
    (r'^$', 'drinkcounter.views.index')
)
